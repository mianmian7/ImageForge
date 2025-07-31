"""
Main View for ImagePass GUI
Acts as a coordinator for all UI managers
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from architecture.interfaces import IUIComponent
from architecture.events import EventBus
from architecture.di import inject
from core.config import Config
from gui.managers.preview_manager import PreviewManager
from gui.managers.process_control_manager import ProcessControlManager
from gui.managers.file_manager_view import FileManagerView
from gui.managers.status_bar_manager import StatusBarManager


class MainView(IUIComponent):
    """Main view of the application, coordinating all UI components"""
    
    def __init__(self, root: tk.Tk, config: Config, event_bus: EventBus):
        self.root = root
        self.config = config
        self._event_bus = event_bus
        
        # UI Managers
        self.file_manager_view = FileManagerView(config)
        self.preview_manager = PreviewManager(config)
        self.process_control_manager = ProcessControlManager(config)
        self.status_bar_manager = StatusBarManager(config)
        
        self.set_event_buses()
        
    def set_event_buses(self):
        """Set event buses for all managers"""
        self.file_manager_view.set_event_bus(self._event_bus)
        self.preview_manager.set_event_bus(self._event_bus)
        self.process_control_manager.set_event_bus(self._event_bus)
        self.status_bar_manager.set_event_bus(self._event_bus)
    
    def initialize(self, parent=None):
        """Initialize the main view and all its components"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Initialize all UI managers
        self.file_manager_view.initialize(main_frame)
        self.preview_manager.initialize(main_frame)
        self.process_control_manager.initialize(main_frame)
        self.status_bar_manager.initialize(main_frame)
        
    def update(self, data: any):
        """Update main view (not typically used)"""
        pass
    
    def get_state(self) -> dict:
        """Get the combined state of all UI components"""
        return {
            'file_manager': self.file_manager_view.get_state(),
            'preview': self.preview_manager.get_state(),
            'process_control': self.process_control_manager.get_state(),
            'status_bar': self.status_bar_manager.get_state()
        }
        
    def set_enabled(self, enabled: bool):
        """Enable/disable all UI components"""
        self.file_manager_view.set_enabled(enabled)
        self.preview_manager.set_enabled(enabled)
        self.process_control_manager.set_enabled(enabled)
        self.status_bar_manager.set_enabled(enabled)

    def bind_events(self):
        """Bind main window events (e.g., closing)"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        """Handle window close event"""
        from tkinter import messagebox
        
        if self.process_control_manager.is_processing:
            if messagebox.askokcancel("退出", "正在处理图片，确定要退出吗？"):
                # Stop processing before closing
                self.process_control_manager._on_stop_clicked()
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """Start the main GUI loop"""
        self.bind_events()
        self.root.mainloop()

