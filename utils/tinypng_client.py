"""
TinyPNG API客户端
提供图片压缩功能
"""

import os
import requests
import json
from typing import Optional, Dict, Any

class TinyPNGClient:
    """TinyPNG API客户端类"""
    
    def __init__(self, api_key: str):
        """初始化TinyPNG客户端
        
        Args:
            api_key: TinyPNG API密钥
        """
        self.api_key = api_key
        self.api_url = "https://api.tinify.com/shrink"
        self.last_error = None
        self.session = requests.Session()
        
        # 设置认证头
        self.session.auth = (api_key, '')
        self.session.headers.update({
            'User-Agent': 'ImagePass/1.0'
        })
    
    def compress_image(self, input_path: str, output_path: str) -> bool:
        """压缩单张图片
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            
        Returns:
            bool: 压缩是否成功
        """
        try:
            # 检查输入文件是否存在
            if not os.path.exists(input_path):
                self.last_error = f"输入文件不存在: {input_path}"
                return False
            
            # 读取文件内容
            with open(input_path, 'rb') as f:
                file_data = f.read()
            
            # 发送压缩请求
            response = self.session.post(
                self.api_url,
                data=file_data,
                headers={'Content-Type': 'application/octet-stream'}
            )
            
            # 检查响应状态
            if response.status_code == 201:
                # 获取压缩后的图片URL
                result = response.json()
                output_url = result['output']['url']
                
                # 下载压缩后的图片
                download_response = self.session.get(output_url)
                
                if download_response.status_code == 200:
                    # 保存压缩后的图片
                    with open(output_path, 'wb') as f:
                        f.write(download_response.content)
                    
                    self.last_error = None
                    return True
                else:
                    self.last_error = f"下载压缩图片失败: HTTP {download_response.status_code}"
                    return False
            else:
                error_msg = self._get_error_message(response)
                self.last_error = f"压缩失败: {error_msg}"
                return False
                
        except requests.exceptions.RequestException as e:
            self.last_error = f"网络请求失败: {str(e)}"
            return False
        except Exception as e:
            self.last_error = f"未知错误: {str(e)}"
            return False
    
    def compress_image_with_info(self, input_path: str, output_path: str) -> Optional[Dict[str, Any]]:
        """压缩图片并返回详细信息
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            
        Returns:
            dict: 压缩信息，包含：
                - success: 是否成功
                - input_size: 输入文件大小
                - output_size: 输出文件大小
                - compression_ratio: 压缩比例
                - error: 错误信息
        """
        try:
            # 获取原始文件大小
            input_size = os.path.getsize(input_path)
            
            # 执行压缩
            success = self.compress_image(input_path, output_path)
            
            if success:
                # 获取压缩后文件大小
                output_size = os.path.getsize(output_path)
                
                # 计算压缩比例
                compression_ratio = (1 - output_size / input_size) * 100
                
                return {
                    'success': True,
                    'input_size': input_size,
                    'output_size': output_size,
                    'compression_ratio': compression_ratio,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'input_size': input_size,
                    'output_size': 0,
                    'compression_ratio': 0,
                    'error': self.last_error
                }
                
        except Exception as e:
            return {
                'success': False,
                'input_size': 0,
                'output_size': 0,
                'compression_ratio': 0,
                'error': str(e)
            }
    
    def validate_api_key(self) -> bool:
        """验证API密钥是否有效
        
        Returns:
            bool: API密钥是否有效
        """
        try:
            # 创建一个极小的测试图片数据
            test_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            response = self.session.post(
                self.api_url,
                data=test_data,
                headers={'Content-Type': 'application/octet-stream'}
            )
            
            return response.status_code in [200, 201, 400, 401]
            
        except Exception:
            return False
    
    def get_compression_count(self) -> Optional[int]:
        """获取本月已使用的压缩次数
        
        Returns:
            int: 压缩次数，如果获取失败返回None
        """
        try:
            response = self.session.get("https://api.tinify.com/shrink")
            
            if response.status_code == 200:
                # 从响应头获取压缩计数
                compression_count = response.headers.get('Compression-Count')
                if compression_count:
                    return int(compression_count)
            
            return None
            
        except Exception:
            return None
    
    def get_last_error(self) -> str:
        """获取最后错误信息"""
        return self.last_error
    
    def _get_error_message(self, response: requests.Response) -> str:
        """从响应中获取错误信息
        
        Args:
            response: HTTP响应对象
            
        Returns:
            str: 错误信息
        """
        try:
            if response.status_code == 401:
                return "API密钥无效或已过期"
            elif response.status_code == 429:
                return "API调用频率超出限制"
            elif response.status_code == 400:
                error_data = response.json()
                return error_data.get('error', '请求参数错误')
            elif response.status_code == 415:
                return "不支持的图片格式"
            else:
                return f"HTTP {response.status_code}: {response.reason}"
        except Exception:
            return f"HTTP {response.status_code}: {response.reason}"