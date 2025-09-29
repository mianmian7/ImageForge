"""
日志系统模块
提供统一的日志配置和管理
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


class LoggerManager:
    """日志管理器类"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化日志管理器"""
        if not LoggerManager._initialized:
            self._setup_logger()
            LoggerManager._initialized = True
    
    def _setup_logger(self, 
                      log_level: str = 'INFO', 
                      log_file: str = 'imageforge.log',
                      max_bytes: int = 10 * 1024 * 1024,  # 10 MB
                      backup_count: int = 5):
        """
        配置日志系统
        
        Args:
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: 日志文件路径
            max_bytes: 单个日志文件最大大小（字节）
            backup_count: 保留的备份日志文件数量
        """
        # 创建日志目录
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 配置根日志记录器
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # 清除现有处理器
        logger.handlers.clear()
        
        # 文件处理器（滚动日志）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        logging.info(f"日志系统已初始化，级别: {log_level}, 文件: {log_file}")
    
    @staticmethod
    def get_logger(name: Optional[str] = None) -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称（通常使用 __name__）
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        return logging.getLogger(name)
    
    @staticmethod
    def set_level(level: str):
        """
        设置日志级别
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        logging.getLogger().setLevel(getattr(logging, level.upper(), logging.INFO))
        logging.info(f"日志级别已设置为: {level}")


# 便捷函数
def setup_logging(log_level: str = 'INFO', log_file: str = 'imageforge.log'):
    """
    配置日志系统（便捷函数）
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
    """
    manager = LoggerManager()
    manager._setup_logger(log_level, log_file)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器（便捷函数）
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return LoggerManager.get_logger(name)
