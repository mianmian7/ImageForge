"""
日志和错误处理模块
提供统一的日志记录和错误处理功能
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional, Any
import traceback

class Logger:
    """日志管理类"""
    
    def __init__(self, log_file=None, log_level=logging.INFO):
        """初始化日志管理器
        
        Args:
            log_file: 日志文件路径，None则只输出到控制台
            log_level: 日志级别
        """
        self.logger = logging.getLogger('ImagePass')
        self.logger.setLevel(log_level)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """错误日志"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """严重错误日志"""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """异常日志（包含堆栈跟踪）"""
        self.logger.exception(message)

class ErrorHandler:
    """错误处理类"""
    
    def __init__(self, logger: Optional[Logger] = None):
        """初始化错误处理器
        
        Args:
            logger: 日志管理器实例
        """
        self.logger = logger or Logger()
        self.error_count = 0
        self.last_error = None
    
    def handle_error(self, error: Exception, context: str = "") -> dict:
        """处理错误
        
        Args:
            error: 异常对象
            context: 错误上下文信息
            
        Returns:
            dict: 错误信息字典
        """
        self.error_count += 1
        self.last_error = error
        
        # 获取错误信息
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # 构建完整的错误信息
        full_message = f"错误在 {context}: {error_type}: {error_message}"
        
        # 记录错误日志
        self.logger.error(full_message)
        self.logger.debug(f"完整堆栈跟踪:\n{error_traceback}")
        
        return {
            'error_type': error_type,
            'error_message': error_message,
            'context': context,
            'traceback': error_traceback,
            'full_message': full_message,
            'error_count': self.error_count
        }
    
    def handle_warning(self, message: str, context: str = "") -> dict:
        """处理警告
        
        Args:
            message: 警告消息
            context: 警告上下文
            
        Returns:
            dict: 警告信息字典
        """
        warning_message = f"警告在 {context}: {message}"
        self.logger.warning(warning_message)
        
        return {
            'type': 'warning',
            'message': message,
            'context': context,
            'full_message': warning_message
        }
    
    def validate_file_exists(self, file_path: str, context: str = "") -> bool:
        """验证文件是否存在
        
        Args:
            file_path: 文件路径
            context: 验证上下文
            
        Returns:
            bool: 文件是否存在
        """
        if not os.path.exists(file_path):
            error_msg = f"文件不存在: {file_path}"
            self.handle_warning(error_msg, context)
            return False
        
        if not os.path.isfile(file_path):
            error_msg = f"路径不是文件: {file_path}"
            self.handle_warning(error_msg, context)
            return False
        
        return True
    
    def validate_directory_exists(self, dir_path: str, context: str = "", create: bool = False) -> bool:
        """验证目录是否存在
        
        Args:
            dir_path: 目录路径
            context: 验证上下文
            create: 如果不存在是否创建
            
        Returns:
            bool: 目录是否存在或创建成功
        """
        if not os.path.exists(dir_path):
            if create:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    self.logger.info(f"创建目录: {dir_path}")
                    return True
                except Exception as e:
                    self.handle_error(e, f"{context}: 创建目录失败 {dir_path}")
                    return False
            else:
                error_msg = f"目录不存在: {dir_path}"
                self.handle_warning(error_msg, context)
                return False
        
        if not os.path.isdir(dir_path):
            error_msg = f"路径不是目录: {dir_path}"
            self.handle_warning(error_msg, context)
            return False
        
        return True
    
    def validate_file_readable(self, file_path: str, context: str = "") -> bool:
        """验证文件是否可读
        
        Args:
            file_path: 文件路径
            context: 验证上下文
            
        Returns:
            bool: 文件是否可读
        """
        if not self.validate_file_exists(file_path, context):
            return False
        
        try:
            with open(file_path, 'rb') as f:
                f.read(1)  # 尝试读取一个字节
            return True
        except Exception as e:
            self.handle_error(e, f"{context}: 文件不可读 {file_path}")
            return False
    
    def validate_file_writable(self, file_path: str, context: str = "", create_dir: bool = True) -> bool:
        """验证文件是否可写
        
        Args:
            file_path: 文件路径
            context: 验证上下文
            create_dir: 是否创建目录
            
        Returns:
            bool: 文件是否可写
        """
        # 检查目录是否存在
        dir_path = os.path.dirname(file_path)
        if not self.validate_directory_exists(dir_path, f"{context}: 文件目录", create_dir):
            return False
        
        # 检查文件是否可写
        if os.path.exists(file_path):
            try:
                with open(file_path, 'a') as f:
                    pass
                return True
            except Exception as e:
                self.handle_error(e, f"{context}: 文件不可写 {file_path}")
                return False
        else:
            # 文件不存在，检查目录是否可写
            try:
                test_file = os.path.join(dir_path, '.test_write')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                return True
            except Exception as e:
                self.handle_error(e, f"{context}: 目录不可写 {dir_path}")
                return False
    
    def get_last_error(self) -> Optional[dict]:
        """获取最后错误信息"""
        return {
            'error': self.last_error,
            'error_count': self.error_count
        }
    
    def reset_error_count(self):
        """重置错误计数"""
        self.error_count = 0
        self.last_error = None

class PerformanceMonitor:
    """性能监控类"""
    
    def __init__(self, logger: Optional[Logger] = None):
        """初始化性能监控器
        
        Args:
            logger: 日志管理器实例
        """
        self.logger = logger or Logger()
        self.start_time = None
        self.operations = {}
    
    def start_operation(self, operation_name: str):
        """开始操作计时
        
        Args:
            operation_name: 操作名称
        """
        self.start_time = datetime.now()
        self.operations[operation_name] = {
            'start_time': self.start_time,
            'end_time': None,
            'duration': None
        }
        self.logger.debug(f"开始操作: {operation_name}")
    
    def end_operation(self, operation_name: str) -> Optional[float]:
        """结束操作计时
        
        Args:
            operation_name: 操作名称
            
        Returns:
            float: 操作耗时（秒）
        """
        if operation_name not in self.operations:
            self.logger.warning(f"未找到操作: {operation_name}")
            return None
        
        end_time = datetime.now()
        operation = self.operations[operation_name]
        operation['end_time'] = end_time
        
        if operation['start_time']:
            duration = (end_time - operation['start_time']).total_seconds()
            operation['duration'] = duration
            
            self.logger.info(f"操作完成: {operation_name}, 耗时: {duration:.2f}秒")
            return duration
        
        return None
    
    def get_operation_duration(self, operation_name: str) -> Optional[float]:
        """获取操作耗时
        
        Args:
            operation_name: 操作名称
            
        Returns:
            float: 操作耗时（秒）
        """
        if operation_name in self.operations:
            return self.operations[operation_name].get('duration')
        return None
    
    def get_all_operations(self) -> dict:
        """获取所有操作信息"""
        return self.operations.copy()

# 全局日志和错误处理器实例
logger = Logger(log_file='logs/imagepass.log')
error_handler = ErrorHandler(logger)
performance_monitor = PerformanceMonitor(logger)