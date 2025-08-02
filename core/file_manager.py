"""
文件管理模块
负责文件和目录的读写操作
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

class FileManager:
    """文件管理类"""
    
    def __init__(self, config=None):
        """初始化文件管理器"""
        self.config = config
        self.current_directory = ""
        self.current_files = []
        self.current_file_index = 0
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的图片格式"""
        if self.config:
            return self.config.get_supported_formats()
        return ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
    
    def is_image_file(self, file_path: str) -> bool:
        """检查文件是否为支持的图片格式"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.get_supported_formats()
    
    def select_single_file(self, file_path: str) -> Optional[str]:
        """选择单个文件"""
        if os.path.isfile(file_path) and self.is_image_file(file_path):
            self.current_directory = os.path.dirname(file_path)
            self.current_files = [file_path]
            self.current_file_index = 0
            return file_path
        return None
    
    def select_directory(self, directory_path: str, recursive: bool = True) -> List[str]:
        """选择目录并获取所有支持的图片文件
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归读取子目录
            
        Returns:
            list: 图片文件路径列表
        """
        if not os.path.isdir(directory_path):
            return []
        
        self.current_directory = directory_path
        self.current_files = []
        
        # 遍历目录查找图片文件
        if recursive:
            # 递归遍历所有子目录
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.is_image_file(file_path):
                        self.current_files.append(file_path)
        else:
            # 只遍历当前目录
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path) and self.is_image_file(file_path):
                    self.current_files.append(file_path)
        
        self.current_files.sort()
        self.current_file_index = 0
        return self.current_files
    
    def get_current_file(self) -> Optional[str]:
        """获取当前文件"""
        if self.current_files and 0 <= self.current_file_index < len(self.current_files):
            return self.current_files[self.current_file_index]
        return None
    
    def get_next_file(self) -> Optional[str]:
        """获取下一个文件"""
        if not self.current_files:
            return None
        
        self.current_file_index = (self.current_file_index + 1) % len(self.current_files)
        return self.get_current_file()
    
    def get_previous_file(self) -> Optional[str]:
        """获取上一个文件"""
        if not self.current_files:
            return None
        
        self.current_file_index = (self.current_file_index - 1) % len(self.current_files)
        return self.get_current_file()
    
    def get_file_count(self) -> int:
        """获取文件总数"""
        return len(self.current_files)
    
    def get_current_index(self) -> int:
        """获取当前文件索引"""
        return self.current_file_index
    
    def set_current_index(self, index: int):
        """设置当前文件索引"""
        if 0 <= index < len(self.current_files):
            self.current_file_index = index
    
    def get_output_path(self, input_path: str, output_mode: str, 
                       output_dir: str = None, output_format: str = None) -> str:
        """根据输出模式获取输出路径
        
        Args:
            input_path: 输入文件路径
            output_mode: 输出模式 ('overwrite', 'new_folder', 'custom_dir')
            output_dir: 输出目录（用于 custom_dir 模式）
            output_format: 输出格式（用于格式转换）
            
        Returns:
            str: 输出文件路径
        """
        # 获取文件名和扩展名
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        
        # 如果指定了输出格式，修改文件扩展名
        if output_format and output_format != "保持原格式":
            # 格式映射
            format_extensions = {
                'JPEG': '.jpg',
                'PNG': '.png',
                'WEBP': '.webp',
                'BMP': '.bmp',
                'TIFF': '.tiff'
            }
            ext = format_extensions.get(output_format, ext)
            filename = f"{name}{ext}"
        
        if output_mode == 'overwrite':
            # 覆盖模式：如果格式不同，仍使用原路径（实际处理时会覆盖）
            return input_path
        
        elif output_mode == 'new_folder':
            input_dir = os.path.dirname(input_path)
            output_folder = os.path.join(input_dir, output_dir or 'processed_images')
            
            # 创建输出文件夹
            os.makedirs(output_folder, exist_ok=True)
            return os.path.join(output_folder, filename)
        
        elif output_mode == 'custom_dir' and output_dir:
            os.makedirs(output_dir, exist_ok=True)
            return os.path.join(output_dir, filename)
        
        return input_path
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """创建文件备份"""
        if not os.path.exists(file_path):
            return None
        
        backup_dir = os.path.join(os.path.dirname(file_path), 'backup')
        os.makedirs(backup_dir, exist_ok=True)
        
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        backup_filename = f"{name}_backup{ext}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 如果备份文件已存在，添加时间戳
        if os.path.exists(backup_path):
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"创建备份失败: {e}")
            return None
    
    def get_file_info(self, file_path: str) -> dict:
        """获取文件信息"""
        if not os.path.exists(file_path):
            return {}
        
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'path': file_path,
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'extension': Path(file_path).suffix.lower()
        }