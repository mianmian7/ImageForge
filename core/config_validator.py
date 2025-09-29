"""
配置验证模块
提供配置文件验证功能
"""

import os
from typing import Dict, List, Optional, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


class ConfigValidator:
    """配置验证器类"""
    
    # 支持的图像格式
    SUPPORTED_FORMATS = ['jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp']
    
    # 日志级别
    VALID_LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def __init__(self):
        """初始化配置验证器"""
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_config(self, config) -> Tuple[bool, List[str], List[str]]:
        """
        验证配置对象
        
        Args:
            config: 配置管理器对象
            
        Returns:
            Tuple[bool, List[str], List[str]]: (是否有效, 错误列表, 警告列表)
        """
        self.errors.clear()
        self.warnings.clear()
        
        # 验证处理配置
        self._validate_processing_config(config)
        
        # 验证UI配置
        self._validate_ui_config(config)
        
        # 验证路径配置
        self._validate_paths_config(config)
        
        # 验证日志配置
        self._validate_logging_config(config)
        
        # 验证TinyPNG配置
        self._validate_tinypng_config(config)
        
        is_valid = len(self.errors) == 0
        
        if is_valid:
            logger.info("配置验证通过")
        else:
            logger.error(f"配置验证失败，发现 {len(self.errors)} 个错误")
        
        if self.warnings:
            logger.warning(f"配置验证发现 {len(self.warnings)} 个警告")
        
        return is_valid, self.errors.copy(), self.warnings.copy()
    
    def _validate_processing_config(self, config):
        """验证处理配置"""
        # 验证压缩质量
        try:
            quality = config.get_int('default_compression', 'Settings', 85)
            if not 1 <= quality <= 100:
                self.errors.append("压缩质量必须在 1-100 之间")
        except ValueError:
            self.errors.append("压缩质量必须是整数")
        
        # 验证最大文件大小
        try:
            max_size = config.get_int('max_file_size_mb', 'Settings', 10)
            if max_size <= 0:
                self.errors.append("最大文件大小必须大于 0")
            elif max_size > 100:
                self.warnings.append(f"最大文件大小设置为 {max_size}MB，可能导致内存问题")
        except ValueError:
            self.errors.append("最大文件大小必须是整数")
        
        # 验证支持的格式
        formats_str = config.get('supported_formats', '.jpg,.jpeg,.png,.bmp,.gif,.tiff,.webp', 
                                'Settings')
        # 移除可能的点号前缀
        formats = [f.strip().lstrip('.') for f in formats_str.split(',') if f.strip()]
        
        for fmt in formats:
            if fmt.lower() not in self.SUPPORTED_FORMATS:
                self.warnings.append(f"不支持的图像格式: {fmt}")
    
    def _validate_ui_config(self, config):
        """验证UI配置"""
        # 验证窗口尺寸
        try:
            width = config.get_int('window_width', 'Settings', 1200)
            height = config.get_int('window_height', 'Settings', 800)
            
            if width < 800:
                self.warnings.append(f"窗口宽度 {width} 太小，建议至少 800 像素")
            if height < 600:
                self.warnings.append(f"窗口高度 {height} 太小，建议至少 600 像素")
            
            if width > 3840 or height > 2160:
                self.warnings.append(f"窗口尺寸 {width}x{height} 过大")
                
        except ValueError:
            self.errors.append("窗口尺寸必须是整数")
        
        # 验证预览尺寸（使用 preview_max_width 和 preview_max_height）
        try:
            preview_width = config.get_int('preview_max_width', 'Settings', 400)
            preview_height = config.get_int('preview_max_height', 'Settings', 400)
            
            if preview_width < 100 or preview_height < 100:
                self.warnings.append(f"预览尺寸 {preview_width}x{preview_height} 太小")
            elif preview_width > 1000 or preview_height > 1000:
                self.warnings.append(f"预览尺寸 {preview_width}x{preview_height} 太大，可能影响性能")
        except ValueError:
            self.errors.append("预览尺寸必须是整数")
    
    def _validate_paths_config(self, config):
        """验证路径配置"""
        # 验证输出目录（使用 default_output_folder）
        output_dir = config.get('default_output_folder', 'processed_images', 'Settings')
        if output_dir and output_dir not in ('processed_images', ''):
            # 只验证绝对路径，相对路径会在运行时创建
            if os.path.isabs(output_dir):
                if not os.path.exists(output_dir):
                    try:
                        os.makedirs(output_dir, exist_ok=True)
                        logger.info(f"创建输出目录: {output_dir}")
                    except Exception as e:
                        self.errors.append(f"无法创建输出目录 {output_dir}: {str(e)}")
                elif not os.path.isdir(output_dir):
                    self.errors.append(f"输出路径不是目录: {output_dir}")
                elif not os.access(output_dir, os.W_OK):
                    self.errors.append(f"输出目录没有写入权限: {output_dir}")
    
    def _validate_logging_config(self, config):
        """验证日志配置"""
        # 验证日志级别
        log_level = config.get('log_level', 'INFO', 'Settings').upper()
        if log_level not in self.VALID_LOG_LEVELS:
            self.errors.append(
                f"无效的日志级别: {log_level}, "
                f"有效值: {', '.join(self.VALID_LOG_LEVELS)}"
            )
        
        # 验证日志文件路径
        log_file = config.get('log_file', 'imageforge.log', 'Settings')
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir, exist_ok=True)
                    logger.info(f"创建日志目录: {log_dir}")
                except Exception as e:
                    self.warnings.append(f"无法创建日志目录: {str(e)}")
    
    def _validate_tinypng_config(self, config):
        """验证TinyPNG配置"""
        api_key = config.get('tinypng_api_key', '', 'Settings')
        
        if not api_key or api_key == 'your_tinypng_api_key_here':
            self.warnings.append(
                "TinyPNG API密钥未设置，云端压缩功能将不可用"
            )
        elif len(api_key) < 20:
            # 这是一个警告，不是错误，因为短密钥可能是有效的
            pass
    
    def get_validation_summary(self) -> str:
        """
        获取验证摘要信息
        
        Returns:
            str: 验证摘要
        """
        summary_parts = []
        
        if not self.errors and not self.warnings:
            return "✅ 配置验证通过，无错误或警告"
        
        if self.errors:
            summary_parts.append(f"❌ 发现 {len(self.errors)} 个错误:")
            for i, error in enumerate(self.errors, 1):
                summary_parts.append(f"  {i}. {error}")
        
        if self.warnings:
            summary_parts.append(f"⚠️  发现 {len(self.warnings)} 个警告:")
            for i, warning in enumerate(self.warnings, 1):
                summary_parts.append(f"  {i}. {warning}")
        
        return "\n".join(summary_parts)


def validate_config(config) -> Tuple[bool, str]:
    """
    验证配置（便捷函数）
    
    Args:
        config: 配置管理器对象
        
    Returns:
        Tuple[bool, str]: (是否有效, 验证摘要)
    """
    validator = ConfigValidator()
    is_valid, errors, warnings = validator.validate_config(config)
    summary = validator.get_validation_summary()
    
    return is_valid, summary
