#!/usr/bin/env python3
"""
GUI语法测试脚本
只检查语法是否正确，不实际运行GUI
"""

import sys
import os

# 添加项目根目录到path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 尝试导入各个模块
    print("测试导入 core.config...")
    from core.config import Config
    print("✓ core.config 导入成功")
    
    print("测试导入 gui.main_window...")
    from gui.main_window import ImageProcessorGUI
    print("✓ gui.main_window 导入成功")
    
    print("测试导入 gui.asset_cleaner_panel...")
    from gui.asset_cleaner_panel import AssetCleanerPanel
    print("✓ gui.asset_cleaner_panel 导入成功")
    
    print("\n所有模块导入测试通过！")
    print("GUI布局代码语法正确。")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)
except SyntaxError as e:
    print(f"❌ 语法错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 其他错误: {e}")
    sys.exit(1)