"""
Processing strategies for different image operations
"""

import time
import os
from typing import Dict, Any, Optional
from PIL import Image

from architecture.interfaces import IImageProcessingStrategy
from utils.imagemagick_wrapper import ImageMagickWrapper
from utils.tinypng_client import TinyPNGClient
from processing.models import ProcessingResult, ImageInfo


class ResizeStrategy(IImageProcessingStrategy):
    """Image resize strategy"""
    
    def __init__(self, imagemagick_path=None):
        self.imagemagick = ImageMagickWrapper(imagemagick_path)
        self.last_error = None
    
    def get_name(self) -> str:
        return "resize"
    
    def get_description(self) -> str:
        return "调整图片分辨率"
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        required_keys = ['resize_mode', 'resize_value']
        return all(key in params for key in required_keys)
    
    def process_image(self, input_path: str, output_path: str, 
                     params: Dict[str, Any]) -> ProcessingResult:
        """Process image resize"""
        start_time = time.time()
        
        try:
            # Get original image info
            original_info = self.imagemagick.get_image_info(input_path)
            if not original_info:
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    input_size=0,
                    output_size=0,
                    error="无法获取图片信息"
                )
            
            input_size = original_info['filesize']
            
            # Perform resize
            resize_mode = params['resize_mode']
            resize_value = params['resize_value']
            quality = params.get('quality', 85)
            maintain_aspect = params.get('maintain_aspect', True)
            
            success = False
            if resize_mode == 'percentage':
                success = self.imagemagick.resize_by_percentage(
                    input_path, output_path, resize_value, quality
                )
            elif resize_mode == 'dimensions':
                if isinstance(resize_value, (tuple, list)) and len(resize_value) == 2:
                    width, height = resize_value
                    success = self.imagemagick.resize_by_dimensions(
                        input_path, output_path, width, height, maintain_aspect, quality
                    )
                else:
                    success = self.imagemagick.resize_by_dimensions(
                        input_path, output_path, resize_value, None, maintain_aspect, quality
                    )
            
            if success:
                # Get result info
                output_size = os.path.getsize(output_path)
                processing_time = time.time() - start_time
                
                return ProcessingResult(
                    success=True,
                    input_path=input_path,
                    output_path=output_path,
                    input_size=input_size,
                    output_size=output_size,
                    processing_time=processing_time,
                    metadata={'original_info': original_info}
                )
            else:
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    input_size=input_size,
                    output_size=0,
                    error=self.imagemagick.get_last_error()
                )
                
        except Exception as e:
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                input_size=0,
                output_size=0,
                error=str(e)
            )


class CompressStrategy(IImageProcessingStrategy):
    """Image compression strategy using TinyPNG"""
    
    def __init__(self, api_key: str = None):
        self.tinypng = TinyPNGClient(api_key) if api_key else None
        self.last_error = None
    
    def get_name(self) -> str:
        return "compress"
    
    def get_description(self) -> str:
        return "使用TinyPNG压缩图片"
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        # No specific parameters required for compression
        return True
    
    def process_image(self, input_path: str, output_path: str, 
                     params: Dict[str, Any]) -> ProcessingResult:
        """Process image compression"""
        start_time = time.time()
        
        if not self.tinypng:
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                input_size=0,
                output_size=0,
                error="TinyPNG客户端未初始化"
            )
        
        try:
            # Get input file size
            input_size = os.path.getsize(input_path)
            
            # Compress with TinyPNG
            result = self.tinypng.compress_image_with_info(input_path, output_path)
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=result['success'],
                input_path=input_path,
                output_path=output_path,
                input_size=input_size,
                output_size=result.get('output_size', 0),
                error=result.get('error'),
                compression_ratio=result.get('compression_ratio'),
                processing_time=processing_time,
                metadata=result
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                input_size=0,
                output_size=0,
                error=str(e)
            )


class FormatConversionStrategy(IImageProcessingStrategy):
    """Image format conversion strategy"""
    
    def __init__(self, imagemagick_path=None):
        self.imagemagick = ImageMagickWrapper(imagemagick_path)
        self.last_error = None
    
    def get_name(self) -> str:
        return "format_conversion"
    
    def get_description(self) -> str:
        return "转换图片格式"
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        return 'output_format' in params
    
    def process_image(self, input_path: str, output_path: str, 
                     params: Dict[str, Any]) -> ProcessingResult:
        """Process image format conversion"""
        start_time = time.time()
        
        try:
            # Get original image info
            original_info = self.imagemagick.get_image_info(input_path)
            if not original_info:
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    input_size=0,
                    output_size=0,
                    error="无法获取图片信息"
                )
            
            input_size = original_info['filesize']
            output_format = params['output_format']
            quality = params.get('quality', 85)
            
            # Convert format
            success = self.imagemagick.convert_format(
                input_path, output_path, output_format, quality
            )
            
            if success:
                # Get result info
                output_size = os.path.getsize(output_path)
                processing_time = time.time() - start_time
                
                return ProcessingResult(
                    success=True,
                    input_path=input_path,
                    output_path=output_path,
                    input_size=input_size,
                    output_size=output_size,
                    processing_time=processing_time,
                    metadata={'original_info': original_info, 'output_format': output_format}
                )
            else:
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    input_size=input_size,
                    output_size=0,
                    error=self.imagemagick.get_last_error()
                )
                
        except Exception as e:
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                input_size=0,
                output_size=0,
                error=str(e)
            )


class OptimizeStrategy(IImageProcessingStrategy):
    """Image optimization strategy"""
    
    def __init__(self, imagemagick_path=None):
        self.imagemagick = ImageMagickWrapper(imagemagick_path)
        self.last_error = None
    
    def get_name(self) -> str:
        return "optimize"
    
    def get_description(self) -> str:
        return "优化图片（不改变尺寸）"
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        return True
    
    def process_image(self, input_path: str, output_path: str, 
                     params: Dict[str, Any]) -> ProcessingResult:
        """Process image optimization"""
        start_time = time.time()
        
        try:
            # Get original image info
            original_info = self.imagemagick.get_image_info(input_path)
            if not original_info:
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    input_size=0,
                    output_size=0,
                    error="无法获取图片信息"
                )
            
            input_size = original_info['filesize']
            quality = params.get('quality', 85)
            
            # Optimize image
            success = self.imagemagick.optimize_image(
                input_path, output_path, quality
            )
            
            if success:
                # Get result info
                output_size = os.path.getsize(output_path)
                processing_time = time.time() - start_time
                
                return ProcessingResult(
                    success=True,
                    input_path=input_path,
                    output_path=output_path,
                    input_size=input_size,
                    output_size=output_size,
                    processing_time=processing_time,
                    metadata={'original_info': original_info}
                )
            else:
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    input_size=input_size,
                    output_size=0,
                    error=self.imagemagick.get_last_error()
                )
                
        except Exception as e:
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                input_size=0,
                output_size=0,
                error=str(e)
            )