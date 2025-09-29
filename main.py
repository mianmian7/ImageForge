#!/usr/bin/env python3
"""
ImageForge - Python GUI Image Processor
主程序入口文件
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import ImageProcessorGUI
from core.config import Config
from core.config_validator import validate_config
from utils.logger import setup_logging, get_logger

# 初始化日志系统
setup_logging(log_level='INFO', log_file='imageforge.log')
logger = get_logger(__name__)

def main():
    """主程序入口函数"""
    try:
        # 初始化配置
        config = Config()
        
        # 验证配置
        is_valid, validation_summary = validate_config(config)
        if not is_valid:
            logger.error(f"配置验证失败:\n{validation_summary}")
            messagebox.showerror("配置错误", validation_summary)
            sys.exit(1)
        elif validation_summary:
            logger.info(f"配置验证结果:\n{validation_summary}")
        
        # 创建主窗口
        root = tk.Tk()
        root.title("ImageForge - 图像处理器")
        root.geometry(f"{config.get('window_width', '1200')}x{config.get('window_height', '800')}")
        
        # 设置窗口图标
        icon_path = get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                # 设置窗口图标（支持.ico格式）
                root.iconbitmap(icon_path)
                logger.info(f"Window icon set from: {icon_path}")
            except Exception as icon_error:
                logger.warning(f"Warning: Could not set window icon: {icon_error}")
        
        # 创建应用实例
        app = ImageProcessorGUI(root, config)
        
        # 启动GUI主循环
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"程序启动失败: {str(e)}", exc_info=True)
        messagebox.showerror("启动错误", f"程序启动失败: {str(e)}")
        sys.exit(1)

def get_resource_path(relative_path):
    """获取资源文件的路径，支持开发环境和打包后的环境"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    main()