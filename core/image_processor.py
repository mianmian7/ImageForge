"""
图片处理核心模块
整合各种图片处理功能
"""

import os
import threading
from typing import Dict, List, Optional, Callable, Any
from utils.pillow_wrapper import PillowWrapper
from utils.tinypng_client import TinyPNGClient
from core.file_manager import FileManager

class ImageProcessor:
    """图片处理核心类"""
    
    def __init__(self, config=None):
        """初始化图片处理器"""
        self.config = config
        self.file_manager = FileManager(config)
        self.pillow = PillowWrapper()
        self.tinypng = None
        self.processing_callback = None
        self.stop_processing = False
        
        # 初始化TinyPNG客户端
        if config:
            api_key = config.get_tinypng_api_key()
            if api_key and api_key != 'your_tinypng_api_key_here':
                self.tinypng = TinyPNGClient(api_key)
    
    def set_processing_callback(self, callback: Callable[[str, int, int], None]):
        """设置处理进度回调函数
        
        Args:
            callback: 回调函数，参数为 (文件路径, 当前进度, 总进度)
        """
        self.processing_callback = callback
    
    def stop_all_processing(self):
        """停止所有处理任务"""
        self.stop_processing = True
    
    def resize_image(self, input_path: str, output_path: str, 
                    resize_mode: str, resize_value, 
                    quality: int = 85, maintain_aspect: bool = True) -> Dict[str, Any]:
        """调整图片大小
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            resize_mode: 调整模式 ('percentage' 或 'dimensions')
            resize_value: 调整值 (百分比或尺寸)
            quality: 图片质量
            maintain_aspect: 是否保持宽高比 (True=保持比例，False=强制调整)
            
        Returns:
            dict: 处理结果
        """
        try:
            # 获取原始图片信息
            original_info = self.pillow.get_image_info(input_path)
            if not original_info:
                return {
                    'success': False,
                    'error': '无法获取图片信息',
                    'input_size': 0,
                    'output_size': 0
                }
            
            input_size = original_info['filesize']
            
            # 执行调整大小
            if resize_mode == 'percentage':
                success = self.pillow.resize_by_percentage(
                    input_path, output_path, resize_value, quality
                )
            elif resize_mode == 'dimensions':
                if isinstance(resize_value, (tuple, list)) and len(resize_value) == 2:
                    width, height = resize_value
                    success = self.pillow.resize_by_dimensions(
                        input_path, output_path, width, height, maintain_aspect, quality
                    )
                else:
                    success = self.pillow.resize_by_dimensions(
                        input_path, output_path, resize_value, None, maintain_aspect, quality
                    )
            else:
                return {
                    'success': False,
                    'error': '不支持的调整模式',
                    'input_size': input_size,
                    'output_size': 0
                }
            
            if success:
                # 获取处理后图片信息
                output_size = os.path.getsize(output_path)
                
                return {
                    'success': True,
                    'error': None,
                    'input_size': input_size,
                    'output_size': output_size,
                    'compression_ratio': (1 - output_size / input_size) * 100,
                    'original_info': original_info
                }
            else:
                return {
                    'success': False,
                    'error': self.pillow.get_last_error(),
                    'input_size': input_size,
                    'output_size': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_size': 0,
                'output_size': 0
            }
    
    def compress_image_tinypng(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """使用TinyPNG压缩图片
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            
        Returns:
            dict: 压缩结果
        """
        if not self.tinypng:
            return {
                'success': False,
                'error': 'TinyPNG客户端未初始化',
                'input_size': 0,
                'output_size': 0
            }
        
        return self.tinypng.compress_image_with_info(input_path, output_path)
    
    def compress_image_pillow(self, input_path: str, output_path: str, 
                            quality: int = 85, mode: str = "optimize", 
                            scale: int = None) -> Dict[str, Any]:
        """使用Pillow压缩图片
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            quality: 压缩质量 (1-100)
            mode: 压缩模式 ('optimize' 或 'resize_optimize')
            scale: 缩放比例 (仅在resize_optimize模式下有效)
            
        Returns:
            dict: 压缩结果
        """
        try:
            # 获取原始图片信息
            original_info = self.pillow.get_image_info(input_path)
            if not original_info:
                return {
                    'success': False,
                    'error': '无法获取图片信息',
                    'input_size': 0,
                    'output_size': 0
                }
            
            input_size = original_info['filesize']
            
            # 执行压缩
            if mode == "optimize":
                # 纯质量优化压缩
                success = self.pillow.optimize_image(input_path, output_path, quality)
            elif mode == "resize_optimize" and scale:
                # 缩放+质量优化压缩
                success = self.pillow.resize_by_percentage(input_path, output_path, scale, quality)
            else:
                return {
                    'success': False,
                    'error': '不支持的压缩模式或缺少缩放参数',
                    'input_size': input_size,
                    'output_size': 0
                }
            
            if success:
                # 获取处理后图片信息
                output_size = os.path.getsize(output_path)
                
                return {
                    'success': True,
                    'error': None,
                    'input_size': input_size,
                    'output_size': output_size,
                    'compression_ratio': (1 - output_size / input_size) * 100,
                    'original_info': original_info
                }
            else:
                return {
                    'success': False,
                    'error': self.pillow.get_last_error(),
                    'input_size': input_size,
                    'output_size': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_size': 0,
                'output_size': 0
            }
    
    def convert_image_format(self, input_path: str, output_path: str, 
                           output_format: str, quality: int = 85) -> Dict[str, Any]:
        """转换图片格式
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            output_format: 输出格式
            quality: 图片质量 (仅对支持质量的格式有效)
            
        Returns:
            dict: 转换结果
        """
        try:
            # 获取原始图片信息
            original_info = self.pillow.get_image_info(input_path)
            if not original_info:
                return {
                    'success': False,
                    'error': '无法获取图片信息',
                    'input_size': 0,
                    'output_size': 0
                }
            
            input_size = original_info['filesize']
            
            # 执行格式转换
            success = self.pillow.convert_format(input_path, output_path, output_format, quality)
            
            if success:
                # 获取处理后图片信息
                output_size = os.path.getsize(output_path)
                
                return {
                    'success': True,
                    'error': None,
                    'input_size': input_size,
                    'output_size': output_size,
                    'compression_ratio': (1 - output_size / input_size) * 100,
                    'original_info': original_info
                }
            else:
                return {
                    'success': False,
                    'error': self.pillow.get_last_error(),
                    'input_size': input_size,
                    'output_size': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_size': 0,
                'output_size': 0
            }
    
    def process_single_image(self, input_path: str, output_path: str, 
                           process_type: str, process_params: Dict[str, Any]) -> Dict[str, Any]:
        """处理单张图片
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            process_type: 处理类型 ('resize', 'compress', 'pillow_compress', 'format_convert')
            process_params: 处理参数
            
        Returns:
            dict: 处理结果
        """
        try:
            if process_type == 'resize':
                return self.resize_image(
                    input_path, output_path,
                    process_params.get('resize_mode', 'percentage'),
                    process_params.get('resize_value', 50),
                    process_params.get('quality', 85),
                    process_params.get('maintain_aspect', True)
                )
            elif process_type == 'compress':
                return self.compress_image_tinypng(input_path, output_path)
            elif process_type == 'pillow_compress':
                return self.compress_image_pillow(
                    input_path, output_path,
                    process_params.get('quality', 85),
                    process_params.get('mode', 'optimize'),
                    process_params.get('scale')
                )
            elif process_type == 'format_convert':
                return self.convert_image_format(
                    input_path, output_path,
                    process_params.get('output_format', 'JPEG'),
                    process_params.get('quality', 85)
                )
            else:
                return {
                    'success': False,
                    'error': f'不支持的处理类型: {process_type}',
                    'input_size': 0,
                    'output_size': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_size': 0,
                'output_size': 0
            }
    
    def process_multiple_images(self, input_paths: List[str], output_mode: str,
                              process_type: str, process_params: Dict[str, Any],
                              output_dir: str = None) -> List[Dict[str, Any]]:
        """批量处理图片
        
        Args:
            input_paths: 输入图片路径列表
            output_mode: 输出模式
            process_type: 处理类型
            process_params: 处理参数
            output_dir: 输出目录
            
        Returns:
            list: 处理结果列表
        """
        results = []
        total_files = len(input_paths)
        
        for i, input_path in enumerate(input_paths):
            if self.stop_processing:
                break
            
            try:
                # 获取输出路径
                output_path = self.file_manager.get_output_path(
                    input_path, output_mode, output_dir
                )
                
                # 处理图片
                result = self.process_single_image(
                    input_path, output_path, process_type, process_params
                )
                
                # 添加文件信息
                result['input_path'] = input_path
                result['output_path'] = output_path
                result['file_index'] = i
                
                results.append(result)
                
                # 调用进度回调
                if self.processing_callback:
                    self.processing_callback(input_path, i + 1, total_files)
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'input_path': input_path,
                    'output_path': '',
                    'input_size': 0,
                    'output_size': 0,
                    'file_index': i
                })
        
        # 重置停止标志
        self.stop_processing = False
        
        return results
    
    def get_image_info(self, image_path: str) -> Optional[Dict[str, Any]]:
        """获取图片信息
        
        Args:
            image_path: 图片路径
            
        Returns:
            dict: 图片信息
        """
        return self.pillow.get_image_info(image_path)
    
    def validate_tinypng_api_key(self, api_key: str) -> bool:
        """验证TinyPNG API密钥
        
        Args:
            api_key: API密钥
            
        Returns:
            bool: 是否有效
        """
        try:
            client = TinyPNGClient(api_key)
            return client.validate_api_key()
        except Exception:
            return False
    
    def set_tinypng_api_key(self, api_key: str):
        """设置TinyPNG API密钥
        
        Args:
            api_key: API密钥
        """
        if api_key and api_key != 'your_tinypng_api_key_here':
            self.tinypng = TinyPNGClient(api_key)
        else:
            self.tinypng = None