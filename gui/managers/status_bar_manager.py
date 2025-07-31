"""
Status Bar Manager for ImagePass GUI
Handles status bar and progress display
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any

from architecture.interfaces import IUIComponent
from architecture.events import EventBus, EventTypes, subscribe_to
from architecture.di import inject


class StatusBarManager(IUIComponent):
    """Manages the status bar and progress display"""
    
    def __init__(self, config=None):
        self._event_bus: Optional[EventBus] = None
        self._parent = None
        
        # UI components
        self.status_label = None
        self.progress_var = None
        self.progress_bar = None
        
    @inject('event_manager')
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for communication"""
        self._event_bus = event_bus
        
        # Subscribe to events
        event_bus.subscribe(EventTypes.PROCESSING_STARTED, self._on_processing_started)
        event_bus.subscribe(EventTypes.PROCESSING_PROGRESS, self._on_processing_progress)
        event_bus.subscribe(EventTypes.PROCESSING_COMPLETE, self._on_processing_complete)
        event_bus.subscribe(EventTypes.PROCESSING_ERROR, self._on_processing_error)
        event_bus.subscribe(EventTypes.PROCESSING_STOPPED, self._on_processing_stopped)
        event_bus.subscribe(EventTypes.FILE_SELECTED, self._on_file_selected)
        event_bus.subscribe(EventTypes.FILES_LOADED, self._on_files_loaded)
    
    def initialize(self, parent):
        """Initialize status bar components"""
        self._parent = parent
        self._create_status_bar_ui()
    
    def _create_status_bar_ui(self):
        """Create status bar user interface"""
        status_frame = ttk.Frame(self._parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="就绪", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
    
    def update(self, data: Any):
        """Update status bar with new data"""
        if isinstance(data, str):
            self.set_status(data)
        elif isinstance(data, dict):
            if 'status' in data:
                self.set_status(data['status'])
            if 'progress' in data:
                self.set_progress(data['progress'])
    
    def get_state(self) -> Dict[str, Any]:
        """Get current status bar state"""
        return {
            'status_text': self.status_label.cget("text"),
            'progress_value': self.progress_var.get()
        }
    
    def set_enabled(self, enabled: bool):
        """Enable/disable status bar components"""
        state = tk.NORMAL if enabled else tk.DISABLED
        if self.status_label:
            self.status_label.config(state=state)
        if self.progress_bar:
            # Progress bar doesn't have a disabled state, but we can hide it
            if enabled:
                self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
            else:
                self.progress_bar.pack_forget()
    
    def set_status(self, text: str):
        """Set status label text"""
        if self.status_label:
            self.status_label.config(text=text)
    
    def set_progress(self, value: float):
        """Set progress bar value"""
        if self.progress_var:
            self.progress_var.set(value)
    
    def reset(self):
        """Reset status bar to default state"""
        self.set_status("就绪")
        self.set_progress(0)
    
    # Event handlers
    def _on_processing_started(self, event):
        """Handle processing started event"""
        self.set_status("正在处理...")
        self.set_progress(0)
    
    def _on_processing_progress(self, event):
        """Handle processing progress event"""
        if event.data:
            current = event.data.get('current', 0)
            total = event.data.get('total', 1)
            file_path = event.data.get('file_path', '')
            
            progress = (current / total) * 100
            self.set_progress(progress)
            
            status_text = f"正在处理: {file_path} ({current}/{total})"
            self.set_status(status_text)
    
    def _on_processing_complete(self, event):
        """Handle processing complete event"""
        if event.data and 'summary' in event.data:
            self.set_status(event.data['summary'])
        else:
            self.set_status("处理完成")
        self.set_progress(100)
    
    def _on_processing_error(self, event):
        """Handle processing error event"""
        if event.data and 'error' in event.data:
            self.set_status(f"处理失败: {event.data['error']}")
        else:
            self.set_status("处理失败")
        self.set_progress(0)
    
    def _on_processing_stopped(self, event):
        """Handle processing stopped event"""
        self.set_status("处理已停止")
        self.set_progress(0)
    
    def _on_file_selected(self, event):
        """Handle file selected event"""
        if event.data and 'file_path' in event.data:
            self.set_status(f"已加载: {event.data['file_path']}")
            self.set_progress(0)
    
    def _on_files_loaded(self, event):
        """Handle files loaded event"""
        if event.data and 'file_count' in event.data:
            self.set_status(f"已加载 {event.data['file_count']} 个文件")
            self.set_progress(0)