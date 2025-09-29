"""
状态栏管理器模块
管理状态栏和进度显示
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class StatusBarManager:
    """状态栏管理器类"""
    
    def __init__(self, parent: tk.Widget):
        """
        初始化状态栏管理器
        
        Args:
            parent: 父窗口组件
        """
        self.parent = parent
        self.status_frame = None
        self.status_label = None
        self.progress_bar = None
        self.progress_var = tk.DoubleVar()
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """创建状态栏组件"""
        self.status_frame = ttk.Frame(self.parent)
        
        self.status_label = ttk.Label(self.status_frame, text="就绪", relief=tk.SUNKEN)
        
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            variable=self.progress_var,
            maximum=100,
            length=200
        )
    
    def _setup_layout(self):
        """设置组件布局"""
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
    
    def set_status(self, text: str):
        """
        设置状态文本
        
        Args:
            text: 状态文本
        """
        self.status_label.config(text=text)
        logger.debug(f"状态更新: {text}")
    
    def set_progress(self, percentage: float):
        """
        设置进度条百分比
        
        Args:
            percentage: 进度百分比 (0-100)
        """
        self.progress_var.set(percentage)
    
    def reset_progress(self):
        """重置进度条"""
        self.progress_var.set(0)
    
    def grid(self, **kwargs):
        """放置状态栏到指定位置"""
        self.status_frame.grid(**kwargs)