"""
ImageMagick封装模块
提供图片分辨率调整功能
"""

import os
from wand.image import Image
from wand.exceptions import WandException
from typing import Tuple, Optional

class ImageMagickWrapper:
    """ImageMagick操作封装类"""
    
    def __init__(self, imagemagick_path=None):
        """初始化ImageMagick封装器"""
        self.imagemagick_path = imagemagick_path
        self.last_error = None
    
    def resize_by_percentage(self, input_path: str, output_path: str, 
                           percentage: float, quality: int = 85) -> bool:
        """按百分比调整图片大小
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            percentage: 缩放百分比 (50表示50%)
            quality: 图片质量 (1-100)
            
        Returns:
            bool: 处理是否成功
        """
        try:
            with Image(filename=input_path) as img:
                # 计算新尺寸
                new_width = int(img.width * percentage / 100)
                new_height = int(img.height * percentage / 100)
                
                # 调整大小
                img.resize(new_width, new_height)
                
                # 设置质量
                img.compression_quality = quality
                
                # 保存图片
                img.save(filename=output_path)
                
            return True
            
        except WandException as e:
            self.last_error = f"ImageMagick处理失败: {str(e)}"
            return False
        except Exception as e:
            self.last_error = f"未知错误: {str(e)}"
            return False
    
    def resize_by_dimensions(self, input_path: str, output_path: str, 
                           width: int, height: int = None, 
                           maintain_aspect: bool = True, 
                           quality: int = 85) -> bool:
        """按指定尺寸调整图片大小
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            width: 目标宽度
            height: 目标高度 (None表示按比例计算)
            maintain_aspect: 是否保持宽高比
            quality: 图片质量 (1-100)
            
        Returns:
            bool: 处理是否成功
        """
        try:
            with Image(filename=input_path) as img:
                original_width = img.width
                original_height = img.height
                
                if maintain_aspect:
                    if height is None:
                        # 只指定宽度，按比例计算高度
                        ratio = width / original_width
                        height = int(original_height * ratio)
                    elif width is None:
                        # 只指定高度，按比例计算宽度
                        ratio = height / original_height
                        width = int(original_width * ratio)
                    else:
                        # 指定宽高，选择保持比例的缩放方式
                        width_ratio = width / original_width
                        height_ratio = height / original_height
                        ratio = min(width_ratio, height_ratio)
                        width = int(original_width * ratio)
                        height = int(original_height * ratio)
                
                # 调整大小
                img.resize(width, height)
                
                # 设置质量
                img.compression_quality = quality
                
                # 保存图片
                img.save(filename=output_path)
                
            return True
            
        except WandException as e:
            self.last_error = f"ImageMagick处理失败: {str(e)}"
            return False
        except Exception as e:
            self.last_error = f"未知错误: {str(e)}"
            return False
    
    def get_image_info(self, image_path: str) -> Optional[dict]:
        """获取图片信息
        
        Args:
            image_path: 图片路径
            
        Returns:
            dict: 图片信息字典
        """
        try:
            with Image(filename=image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'filesize': os.path.getsize(image_path),
                    'resolution': img.resolution
                }
        except Exception as e:
            self.last_error = f"获取图片信息失败: {str(e)}"
            return None
    
    def convert_format(self, input_path: str, output_path: str, 
                      output_format: str, quality: int = 85) -> bool:
        """转换图片格式
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            output_format: 输出格式 (如 'JPEG', 'PNG')
            quality: 图片质量 (1-100)
            
        Returns:
            bool: 转换是否成功
        """
        try:
            with Image(filename=input_path) as img:
                img.format = output_format
                img.compression_quality = quality
                img.save(filename=output_path)
            return True
        except Exception as e:
            self.last_error = f"格式转换失败: {str(e)}"
            return False
    
    def optimize_image(self, input_path: str, output_path: str, 
                      quality: int = 85) -> bool:
        """优化图片（不改变尺寸）
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            quality: 图片质量 (1-100)
            
        Returns:
            bool: 优化是否成功
        """
        try:
            with Image(filename=input_path) as img:
                # 保持原尺寸，只优化质量
                img.compression_quality = quality
                
                # 应用一些优化
                img.strip()  # 移除元数据
                
                img.save(filename=output_path)
            return True
        except Exception as e:
            self.last_error = f"图片优化失败: {str(e)}"
            return False
    
    def get_last_error(self) -> str:
        """获取最后错误信息"""
        return self.last_error
    
    def is_imagemagick_available(self) -> bool:
        """检查ImageMagick是否可用"""
        try:
            import wand
            return True
        except ImportError:
            return False