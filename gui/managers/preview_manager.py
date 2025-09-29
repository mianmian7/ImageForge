"""
预览管理器模块
管理图像预览和显示
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from typing import Optional
from utils.logger import get_logger
from utils.common_utils import get_image_info_text

logger = get_logger(__name__)


class PreviewManager:
    """图像预览管理器类"""
    
    def __init__(self, parent: tk.Widget, config, processor):
        """
        初始化预览管理器
        
        Args:
            parent: 父窗口组件
            config: 配置管理器
            processor: 图像处理器实例
        """
        self.parent = parent
        self.config = config
        self.processor = processor
        
        # 图像引用（防止垃圾回收）
        self.current_image_tk = None
        self.processed_image_tk = None
        
        # 组件
        self.preview_frame = None
        self.original_label = None
        self.processed_label = None
        self.original_resolution_label = None
        self.processed_resolution_label = None
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """创建预览组件"""
        self.preview_frame = ttk.LabelFrame(self.parent, text="图片预览", padding="10")
        
        # 预览容器
        preview_container = ttk.Frame(self.preview_frame)
        
        # 原图预览
        original_frame = ttk.LabelFrame(preview_container, text="原图", padding="5")
        self.original_label = ttk.Label(
            original_frame, 
            text="请选择图片文件",
            relief=tk.SUNKEN,
            anchor=tk.CENTER
        )
        self.original_label.pack(fill=tk.BOTH, expand=True)
        
        self.original_resolution_label = ttk.Label(
            original_frame,
            text="",
            foreground="gray",
            font=("Arial", 9)
        )
        self.original_resolution_label.pack(pady=(2, 0))
        
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 处理后预览
        processed_frame = ttk.LabelFrame(preview_container, text="处理后", padding="5")
        self.processed_label = ttk.Label(
            processed_frame,
            text="等待处理",
            relief=tk.SUNKEN,
            anchor=tk.CENTER
        )
        self.processed_label.pack(fill=tk.BOTH, expand=True)
        
        self.processed_resolution_label = ttk.Label(
            processed_frame,
            text="",
            foreground="gray",
            font=("Arial", 9)
        )
        self.processed_resolution_label.pack(pady=(2, 0))
        
        processed_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        preview_container.pack(fill=tk.BOTH, expand=True)
        preview_container.columnconfigure(0, weight=1)
        preview_container.columnconfigure(1, weight=1)
    
    def _setup_layout(self):
        """设置组件布局"""
        # 布局在 _create_widgets 中完成
        pass
    
    def display_image(self, image_path: str, label_widget: ttk.Label, is_original: bool = True):
        """
        在指定标签中显示图片
        
        Args:
            image_path: 图像文件路径
            label_widget: 显示图像的标签组件
            is_original: 是否是原图
        """
        try:
            # 打开图片
            pil_image = Image.open(image_path)
            
            # 获取标签大小
            label_widget.update_idletasks()
            label_width = label_widget.winfo_width()
            label_height = label_widget.winfo_height()
            
            # 计算缩放比例
            max_width, max_height = self.config.get_preview_size()
            if label_width > 1 and label_height > 1:
                max_width = min(max_width, label_width - 10)
                max_height = min(max_height, label_height - 10)
            
            # 调整图片大小
            pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # 转换为Tkinter格式
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # 显示图片
            label_widget.config(image=tk_image, text="")
            
            # 保存引用防止被垃圾回收
            if is_original:
                self.current_image_tk = tk_image
            else:
                self.processed_image_tk = tk_image
            
            # 更新图片信息显示
            info_text = get_image_info_text(self.processor, image_path)
            if is_original:
                self.original_resolution_label.config(text=info_text)
            else:
                self.processed_resolution_label.config(text=info_text)
                
            logger.debug(f"成功显示图像: {os.path.basename(image_path)}")
                
        except Exception as e:
            logger.error(f"显示图像失败: {image_path}, 错误: {e}")
            label_widget.config(image='', text=f"显示错误: {str(e)}")
            # 清空信息显示
            if is_original:
                self.original_resolution_label.config(text="")
            else:
                self.processed_resolution_label.config(text="")
    
    def display_original(self, image_path: str):
        """
        显示原图
        
        Args:
            image_path: 图像文件路径
        """
        self.display_image(image_path, self.original_label, is_original=True)
    
    def display_processed(self, image_path: str):
        """
        显示处理后的图像
        
        Args:
            image_path: 图像文件路径
        """
        self.display_image(image_path, self.processed_label, is_original=False)
    
    def clear_original(self):
        """清空原图预览"""
        self.original_label.config(image='', text="请选择图片文件")
        self.original_resolution_label.config(text="")
        self.current_image_tk = None
    
    def clear_processed(self):
        """清空处理后预览"""
        self.processed_label.config(image='', text="等待处理")
        self.processed_resolution_label.config(text="")
        self.processed_image_tk = None
    
    def clear_all(self):
        """清空所有预览"""
        self.clear_original()
        self.clear_processed()
    
    def grid(self, **kwargs):
        """放置预览区域到指定位置"""
        self.preview_frame.grid(**kwargs)