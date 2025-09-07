"""
图片处理核心模块
整合各种图片处理功能
"""

import os
import threading
import json
import shutil
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
            # 检查是否需要格式转换
            needs_format_conversion = 'output_format' in process_params
            temp_path = None
            
            if needs_format_conversion:
                # 创建临时文件路径
                temp_dir = os.path.dirname(output_path)
                temp_name = f"temp_{os.path.basename(output_path)}"
                temp_path = os.path.join(temp_dir, temp_name)
                
                # 根据处理类型执行相应的操作，结果存储到临时文件
                if process_type == 'resize':
                    result = self.resize_image(
                        input_path, temp_path,
                        process_params.get('resize_mode', 'percentage'),
                        process_params.get('resize_value', 50),
                        process_params.get('quality', 85),
                        process_params.get('maintain_aspect', True)
                    )
                elif process_type == 'compress':
                    result = self.compress_image_tinypng(input_path, temp_path)
                elif process_type == 'pillow_compress':
                    result = self.compress_image_pillow(
                        input_path, temp_path,
                        process_params.get('quality', 85),
                        process_params.get('mode', 'optimize'),
                        process_params.get('scale')
                    )
                elif process_type == 'format_convert':
                    # 纯格式转换，不做其他处理，直接复制到临时文件
                    import shutil
                    shutil.copy2(input_path, temp_path)
                    
                    # 获取原始文件信息作为结果
                    input_size = os.path.getsize(input_path)
                    result = {
                        'success': True,
                        'error': None,
                        'input_size': input_size,
                        'output_size': input_size,  # 复制阶段大小不变
                        'compression_ratio': 0,
                        'original_info': {}
                    }
                else:
                    return {
                        'success': False,
                        'error': f'不支持的处理类型: {process_type}',
                        'input_size': 0,
                        'output_size': 0
                    }
                
                # 如果前面的处理成功，进行格式转换
                if result['success']:
                    format_result = self.convert_image_format(
                        temp_path, output_path,
                        process_params.get('output_format', 'JPEG'),
                        process_params.get('quality', 85)
                    )
                    
                    # 删除临时文件
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    
                    # 如果格式转换成功，组合结果
                    if format_result['success']:
                        # 检查是否需要删除原文件（覆盖模式且格式转换）
                        if input_path != output_path and os.path.exists(input_path):
                            try:
                                # 获取文件扩展名进行比较
                                input_ext = os.path.splitext(input_path)[1].lower()
                                output_ext = os.path.splitext(output_path)[1].lower()
                                
                                # 如果格式确实发生了转换，删除原文件
                                if input_ext != output_ext:
                                    os.remove(input_path)
                            except Exception as e:
                                # 删除原文件失败不影响整体成功，只记录到error信息中
                                pass
                        
                        # 保留原始输入大小，更新输出大小为最终格式转换后的大小
                        combined_result = {
                            'success': True,
                            'error': None,
                            'input_size': result['input_size'],  # 使用原始输入大小
                            'output_size': format_result['output_size'],  # 使用格式转换后的输出大小
                            'compression_ratio': (1 - format_result['output_size'] / result['input_size']) * 100,
                            'original_info': result.get('original_info', format_result.get('original_info', {}))
                        }
                        
                        # 处理Meta覆盖
                        if process_params.get('meta_override', False):
                            scale_factor = self._get_scale_factor(process_type, process_params)
                            meta_success = self.process_meta_file(input_path, output_path, scale_factor)
                            if meta_success:
                                combined_result['meta_processed'] = True
                            else:
                                combined_result['meta_processed'] = False
                                combined_result['meta_error'] = 'Meta文件处理失败'
                        
                        return combined_result
                    else:
                        # 格式转换失败，返回前面的处理结果但包含格式转换错误
                        result['success'] = False
                        result['error'] = f"前面的处理成功，但格式转换失败: {format_result.get('error', '未知错误')}"
                        return result
                else:
                    # 如果前面的处理失败或只是格式转换，直接返回结果
                    if temp_path and os.path.exists(temp_path) and temp_path != output_path:
                        try:
                            import shutil
                            shutil.move(temp_path, output_path)
                        except:
                            pass
                    return result
            else:
                # 不需要格式转换，直接处理
                result = None
                if process_type == 'resize':
                    result = self.resize_image(
                        input_path, output_path,
                        process_params.get('resize_mode', 'percentage'),
                        process_params.get('resize_value', 50),
                        process_params.get('quality', 85),
                        process_params.get('maintain_aspect', True)
                    )
                elif process_type == 'compress':
                    result = self.compress_image_tinypng(input_path, output_path)
                elif process_type == 'pillow_compress':
                    result = self.compress_image_pillow(
                        input_path, output_path,
                        process_params.get('quality', 85),
                        process_params.get('mode', 'optimize'),
                        process_params.get('scale')
                    )
                else:
                    result = {
                        'success': False,
                        'error': f'不支持的处理类型: {process_type}',
                        'input_size': 0,
                        'output_size': 0
                    }
                
                # 处理Meta覆盖 (仅在处理成功时)
                if result and result.get('success', False) and process_params.get('meta_override', False):
                    scale_factor = self._get_scale_factor(process_type, process_params)
                    meta_success = self.process_meta_file(input_path, output_path, scale_factor)
                    if meta_success:
                        result['meta_processed'] = True
                    else:
                        result['meta_processed'] = False
                        result['meta_error'] = 'Meta文件处理失败'
                
                return result
                
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
                # 获取输出格式
                output_format = process_params.get('output_format')
                
                # 获取输出路径
                output_path = self.file_manager.get_output_path(
                    input_path, output_mode, output_dir, output_format
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
    
    def process_meta_file(self, input_path: str, output_path: str, scale_factor: float = 1.0) -> bool:
        """处理Cocos Creator meta文件
        
        Args:
            input_path: 原始图片路径
            output_path: 输出图片路径  
            scale_factor: 缩放比例 (如50%则传入0.5)
            
        Returns:
            bool: 是否处理成功
        """
        try:
            # 构造meta文件路径
            input_meta_path = input_path + ".meta"
            output_meta_path = output_path + ".meta"
            
            # 检查原始meta文件是否存在
            if not os.path.exists(input_meta_path):
                return False
            
            # 如果输入和输出是同一个文件，直接修改
            if input_meta_path == output_meta_path:
                # 读取原始meta文件
                with open(input_meta_path, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                
                # 处理坐标缩放（如果需要）
                if scale_factor != 1.0:
                    self._scale_meta_coordinates(meta_data, scale_factor)
                
                # 写回同一个文件
                with open(input_meta_path, 'w', encoding='utf-8') as f:
                    json.dump(meta_data, f, indent=2, ensure_ascii=False)
                    
                return True
            else:
                # 读取原始meta文件
                with open(input_meta_path, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                
                # 更新文件格式标识
                input_ext = os.path.splitext(input_path)[1]
                output_ext = os.path.splitext(output_path)[1]
                
                if 'files' in meta_data and input_ext != output_ext:
                    # 替换文件扩展名
                    for i, file_ext in enumerate(meta_data['files']):
                        if file_ext == input_ext:
                            meta_data['files'][i] = output_ext
                
                # 处理顶点坐标缩放
                if scale_factor != 1.0:
                    self._scale_meta_coordinates(meta_data, scale_factor)
                
                # 写入新的meta文件（保留原始UUID）
                with open(output_meta_path, 'w', encoding='utf-8') as f:
                    json.dump(meta_data, f, indent=2, ensure_ascii=False)
                
                # 如果成功创建了新meta文件，删除原meta文件
                if os.path.exists(output_meta_path) and input_meta_path != output_meta_path:
                    try:
                        os.remove(input_meta_path)
                    except Exception as e:
                        print(f"删除原meta文件失败: {e}")
                
                return True
            
        except Exception as e:
            print(f"处理meta文件失败: {e}")
            return False
    
    def _scale_meta_coordinates(self, meta_data: dict, scale_factor: float):
        """缩放meta文件中的顶点坐标
        
        Args:
            meta_data: meta数据字典
            scale_factor: 缩放比例
        """
        def smart_scale(value, factor):
            """智能缩放，保持整数或.5的数值"""
            scaled = value * factor
            # 先四舍五入到0.5的倍数
            rounded = round(scaled * 2) / 2
            # 如果原本就是整数，尽量保持整数
            if abs(rounded - round(rounded)) < 0.001:  # 基本是整数
                return float(round(rounded))
            else:
                return rounded
        
        try:
            # 遍历subMetas寻找spriteFrame
            if 'subMetas' in meta_data:
                for sub_meta in meta_data['subMetas'].values():
                    if sub_meta.get('importer') == 'sprite-frame' and 'userData' in sub_meta:
                        user_data = sub_meta['userData']
                        
                        # 缩放尺寸相关属性（这些必须是整数）
                        size_fields = ['width', 'height', 'rawWidth', 'rawHeight']
                        for field in size_fields:
                            if field in user_data:
                                # 对于尺寸，确保结果是整数且尽量是偶数
                                scaled_size = user_data[field] * scale_factor
                                # 优先保持偶数，有利于2的幂次方
                                rounded_size = round(scaled_size)
                                if rounded_size % 2 != 0 and user_data[field] % 2 == 0:
                                    # 原本是偶数，尽量保持偶数特性
                                    if scaled_size > rounded_size:
                                        rounded_size += 1
                                    else:
                                        rounded_size -= 1
                                        
                                user_data[field] = max(1, rounded_size)  # 确保至少为1
                        
                        # 缩放顶点坐标
                        if 'vertices' in user_data:
                            vertices = user_data['vertices']
                            
                            # 缩放rawPosition（允许.5的数值）
                            if 'rawPosition' in vertices:
                                for i in range(len(vertices['rawPosition'])):
                                    vertices['rawPosition'][i] = smart_scale(
                                        vertices['rawPosition'][i], scale_factor
                                    )
                            
                            # 缩放UV坐标 (保持整数)
                            if 'uv' in vertices:
                                for i in range(len(vertices['uv'])):
                                    vertices['uv'][i] = max(0, round(vertices['uv'][i] * scale_factor))
                            
                            # 缩放minPos和maxPos（允许.5的数值）
                            if 'minPos' in vertices:
                                for i in range(len(vertices['minPos'])):
                                    vertices['minPos'][i] = smart_scale(
                                        vertices['minPos'][i], scale_factor
                                    )
                            
                            if 'maxPos' in vertices:
                                for i in range(len(vertices['maxPos'])):
                                    vertices['maxPos'][i] = smart_scale(
                                        vertices['maxPos'][i], scale_factor
                                    )
                                    
        except Exception as e:
            print(f"缩放meta坐标失败: {e}")
    
    def _get_scale_factor(self, process_type: str, process_params: Dict[str, Any]) -> float:
        """根据处理类型和参数获取缩放比例
        
        Args:
            process_type: 处理类型
            process_params: 处理参数
            
        Returns:
            float: 缩放比例 (1.0表示无缩放)
        """
        if process_type == 'resize':
            resize_mode = process_params.get('resize_mode', 'percentage')
            if resize_mode == 'percentage':
                # 百分比模式，直接返回比例
                percentage = process_params.get('resize_value', 100)
                return percentage / 100.0
            else:
                # 指定尺寸模式，需要从原图计算比例
                # 这里返回1.0，因为需要原图尺寸信息才能计算精确比例
                # 在实际使用时可以传入原图尺寸信息
                return 1.0
        elif process_type == 'pillow_compress':
            # Pillow压缩如果有缩放参数
            if process_params.get('mode') == 'resize_optimize':
                scale = process_params.get('scale', 100)
                return scale / 100.0
        
        # 其他情况不涉及尺寸变化
        return 1.0