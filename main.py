#!/usr/bin/env python3
"""
ImagePass - Python GUI Image Processor
主程序入口文件
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import ImageProcessorGUI
from core.config import Config

def main():
    """主程序入口函数"""
    try:
        # 初始化配置
        config = Config()
        
        # 创建主窗口
        root = tk.Tk()
        root.title("ImagePass - 图像处理器")
        root.geometry(f"{config.get('window_width', '1200')}x{config.get('window_height', '800')}")
        
        # 创建应用实例
        app = ImageProcessorGUI(root, config)
        
        # 启动GUI主循环
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("启动错误", f"程序启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()