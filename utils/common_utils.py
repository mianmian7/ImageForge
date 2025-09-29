"""
公共工具函数模块
提供可复用的工具函数
"""

from typing import Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化后的文件大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_image_info_text(processor, image_path: str) -> str:
    """
    获取图片信息文本（分辨率和文件大小）
    
    Args:
        processor: 图像处理器实例
        image_path: 图像文件路径
        
    Returns:
        str: 图片信息文本
    """
    import os
    
    try:
        resolution = "未知分辨率"
        file_size = "未知大小"
        
        # 获取图片信息
        image_info = processor.get_image_info(image_path)
        if image_info and 'width' in image_info and 'height' in image_info:
            resolution = f"{image_info['width']} × {image_info['height']}"
        
        # 获取文件大小
        if os.path.exists(image_path):
            size_bytes = os.path.getsize(image_path)
            file_size = format_file_size(size_bytes)
        
        return f"{resolution} | {file_size}"
    except Exception as e:
        logger.warning(f"获取图像信息失败: {e}")
        return "信息获取失败"


def calculate_thumbnail_size(original_width: int, original_height: int, 
                            max_width: int, max_height: int) -> Tuple[int, int]:
    """
    计算缩略图尺寸（保持宽高比）
    
    Args:
        original_width: 原始宽度
        original_height: 原始高度
        max_width: 最大宽度
        max_height: 最大高度
        
    Returns:
        Tuple[int, int]: (缩略图宽度, 缩略图高度)
    """
    if original_width <= max_width and original_height <= max_height:
        return (original_width, original_height)
    
    ratio = min(max_width / original_width, max_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    
    return (new_width, new_height)
