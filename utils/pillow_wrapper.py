"""
Pillow图片处理封装模块
提供图片分辨率调整、格式转换、优化等功能
"""

import os
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageOps

class PillowWrapper:
    """Pillow图片处理封装类"""
    
    def __init__(self):
        """初始化Pillow封装器"""
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
            with Image.open(input_path) as img:
                # 计算新尺寸
                new_width = int(img.width * percentage / 100)
                new_height = int(img.height * percentage / 100)
                
                # 调整大小
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 保存图片
                self._save_image_with_quality(resized_img, output_path, quality)
                
            return True
                
        except Exception as e:
            self.last_error = f"Pillow处理失败: {str(e)}"
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
            with Image.open(input_path) as img:
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
                        # 指定宽高，根据maintain_aspect参数选择处理方式
                        if maintain_aspect:
                            # 保持宽高比，选择较小的比例确保图片适应目标尺寸
                            width_ratio = width / original_width
                            height_ratio = height / original_height
                            ratio = min(width_ratio, height_ratio)
                            width = int(original_width * ratio)
                            height = int(original_height * ratio)
                        else:
                            # 不保持宽高比，强制调整到指定尺寸
                            pass
                
                # 调整大小
                resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # 保存图片
                self._save_image_with_quality(resized_img, output_path, quality)
                
            return True
                
        except Exception as e:
            self.last_error = f"Pillow处理失败: {str(e)}"
            return False
    
    def get_image_info(self, image_path: str) -> Optional[Dict[str, Any]]:
        """获取图片信息
        
        Args:
            image_path: 图片路径
            
        Returns:
            dict: 图片信息字典
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'filesize': os.path.getsize(image_path),
                    'mode': img.mode
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
            with Image.open(input_path) as img:
                # 转换模式如果需要
                if output_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                    # JPEG不支持透明度，转换为RGB
                    img = img.convert('RGB')
                elif output_format.upper() == 'PNG' and img.mode not in ('RGBA', 'LA', 'P'):
                    # PNG支持透明度，转换为RGBA保持质量
                    img = img.convert('RGBA')
                
                # 保存为新格式
                self._save_image_with_quality(img, output_path, quality, output_format)
                
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
            with Image.open(input_path) as img:
                # 保持原尺寸，只优化质量
                self._save_image_with_quality(img, output_path, quality)
                
            return True
        except Exception as e:
            self.last_error = f"图片优化失败: {str(e)}"
            return False
    
    def _save_image_with_quality(self, img: Image.Image, output_path: str, 
                               quality: int, format: str = None) -> None:
        """保存图片并指定质量
        
        Args:
            img: PIL图片对象
            output_path: 输出路径
            quality: 图片质量
            format: 图片格式 (None表示自动检测)
        """
        # 确定输出格式
        if format is None:
            # 从文件扩展名推断格式
            ext = os.path.splitext(output_path)[1].lower()
            if ext in ('.jpg', '.jpeg'):
                format = 'JPEG'
            elif ext == '.png':
                format = 'PNG'
            elif ext == '.bmp':
                format = 'BMP'
            elif ext == '.gif':
                format = 'GIF'
            elif ext == '.tiff':
                format = 'TIFF'
            elif ext == '.webp':
                format = 'WEBP'
            else:
                format = 'JPEG'  # 默认格式
        
        # 保存参数
        save_params = {}
        
        if format.upper() in ('JPEG', 'WEBP'):
            save_params['quality'] = quality
            save_params['optimize'] = True
            
            # 增强压缩参数（特别是针对低质量设置）
            if quality <= 30:
                # 极限压缩模式
                save_params['progressive'] = True
                save_params['progression_force'] = True
                if hasattr(img, 'quantize') and img.mode == 'P':
                    # 对于索引色图片，进一步优化颜色数量
                    colors = max(2, 256 // (31 - quality))
                    img = img.quantize(colors=colors)
            elif quality <= 50:
                # 高压缩模式
                save_params['progressive'] = True
                
        elif format.upper() == 'PNG':
            # PNG使用压缩级别而不是质量
            save_params['compress_level'] = min(9, max(0, (100 - quality) // 10))
            save_params['optimize'] = True
            
            # 对于低质量设置，减少颜色深度
            if quality <= 50 and img.mode in ('RGBA', 'RGB'):
                # 转换为P模式（索引色）以获得更好的压缩
                colors = max(2, 256 // ((100 - quality) // 10 + 1))
                img = img.convert('P', palette=Image.Palette.ADAPTIVE, colors=colors)
        
        # 保存图片
        img.save(output_path, format=format, **save_params)
    
    def get_last_error(self) -> str:
        """获取最后错误信息"""
        return self.last_error
    
    def get_processor_info(self) -> Dict[str, Any]:
        """获取处理器信息"""
        return {
            'processor': 'pillow',
            'pillow_available': True,
            'processor_name': 'Pillow'
        }