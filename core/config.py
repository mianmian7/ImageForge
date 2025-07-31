"""
配置管理模块
负责读取和管理应用程序配置
"""

import configparser
import os
from pathlib import Path

class Config:
    """配置管理类"""
    
    def __init__(self, config_file=None):
        """初始化配置管理器"""
        if config_file is None:
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
        
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file, encoding='utf-8')
            else:
                print(f"配置文件不存在: {self.config_file}")
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key, default=None, section='DEFAULT'):
        """获取配置值"""
        try:
            return self.config.get(section, key, fallback=default)
        except Exception as e:
            print(f"获取配置失败: {e}")
            return default
    
    def set(self, key, value, section='DEFAULT'):
        """设置配置值"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, key, str(value))
        except Exception as e:
            print(f"设置配置失败: {e}")
    
    def get_tinypng_api_key(self):
        """获取TinyPNG API密钥"""
        return self.get('tinypng_api_key', '')
    
    def set_tinypng_api_key(self, api_key):
        """设置TinyPNG API密钥"""
        self.set('tinypng_api_key', api_key)
    
    
    def get_supported_formats(self):
        """获取支持的图片格式列表"""
        formats_str = self.get('supported_formats', '.jpg,.jpeg,.png,.bmp,.gif,.tiff,.webp')
        return [f.strip() for f in formats_str.split(',')]
    
    def get_default_output_mode(self):
        """获取默认输出模式"""
        return self.get('default_output_mode', 'new_folder')
    
    def get_window_size(self):
        """获取窗口大小"""
        width = self.get('window_width', '1200')
        height = self.get('window_height', '800')
        return int(width), int(height)
    
    def get_preview_size(self):
        """获取预览图片最大尺寸"""
        width = self.get('preview_max_width', '400')
        height = self.get('preview_max_height', '400')
        return int(width), int(height)