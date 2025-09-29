"""
GUI管理器模块
提供模块化的GUI组件管理
"""

from gui.managers.file_manager_view import FileManagerView
from gui.managers.preview_manager import PreviewManager
from gui.managers.process_control_manager import ProcessControlManager
from gui.managers.status_bar_manager import StatusBarManager

__all__ = [
    'FileManagerView',
    'PreviewManager',
    'ProcessControlManager',
    'StatusBarManager'
]