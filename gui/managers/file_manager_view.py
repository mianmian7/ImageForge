"""
File Manager View for ImagePass GUI
Handles file selection and navigation UI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List, Dict, Any

from architecture.interfaces import IUIComponent
from architecture.events import EventBus, EventTypes, subscribe_to
from architecture.di import inject
from core.config import Config


class FileManagerView(IUIComponent):
    """Manages file selection and navigation UI"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._event_bus: Optional[EventBus] = None
        self._parent = None
        
        # UI components
        self.file_path_var = None
        self.prev_btn = None
        self.next_btn = None
        self.file_count_label = None
        self.recursive_var = None
        self.recursive_hint_label = None
        
        # State
        self.current_files = []
        self.current_file_index = 0
        self.current_directory = ""
        self.recursive_enabled = True
        
    @inject('event_manager')
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for communication"""
        self._event_bus = event_bus
        
        # Subscribe to events
        event_bus.subscribe(EventTypes.CONFIG_CHANGED, self._on_config_changed)
        event_bus.subscribe(EventTypes.NAVIGATION_NEXT, self._on_navigation_next)
        event_bus.subscribe(EventTypes.NAVIGATION_PREVIOUS, self._on_navigation_previous)
    
    def initialize(self, parent):
        """Initialize file manager components"""
        self._parent = parent
        self._create_file_selection_ui()
    
    def _create_file_selection_ui(self):
        """Create file selection user interface"""
        # Create file frame
        file_frame = ttk.LabelFrame(self._parent, text="文件选择", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # File path display
        self.file_path_var = tk.StringVar()
        file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        file_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Selection buttons
        select_file_btn = ttk.Button(file_frame, text="选择文件", command=self._select_single_file)
        select_file_btn.grid(row=0, column=1, padx=(0, 5))
        
        select_folder_btn = ttk.Button(file_frame, text="选择文件夹", command=self._select_directory)
        select_folder_btn.grid(row=0, column=2, padx=(0, 5))
        
        # Navigation buttons
        self.prev_btn = ttk.Button(file_frame, text="上一张", command=self._show_previous_image, state=tk.DISABLED)
        self.prev_btn.grid(row=0, column=3, padx=(0, 5))
        
        self.next_btn = ttk.Button(file_frame, text="下一张", command=self._show_next_image, state=tk.DISABLED)
        self.next_btn.grid(row=0, column=4)
        
        # File count label
        self.file_count_label = ttk.Label(file_frame, text="0/0")
        self.file_count_label.grid(row=0, column=5, padx=(10, 0))
        
        # Recursive options
        recursive_frame = ttk.Frame(file_frame)
        recursive_frame.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.recursive_var = tk.BooleanVar(value=self.recursive_enabled)
        recursive_check = ttk.Checkbutton(recursive_frame, text="递归读取子目录", 
                                        variable=self.recursive_var,
                                        command=self._on_recursive_change)
        recursive_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.recursive_hint_label = ttk.Label(recursive_frame, 
                                            text="(勾选后读取文件夹及其所有子文件夹中的图片)", 
                                            foreground="gray", font=("Arial", 9))
        self.recursive_hint_label.pack(side=tk.LEFT)
        
        # Configure grid weights
        file_frame.columnconfigure(0, weight=1)
    
    def update(self, data: Any):
        """Update file manager with new data"""
        if isinstance(data, str):
            # Assume it's a file path
            self.load_file(data)
        elif isinstance(data, dict):
            if 'file_path' in data:
                self.load_file(data['file_path'])
            if 'files' in data:
                self.load_files(data['files'])
            if 'directory' in data:
                self.load_directory(data['directory'])
    
    def get_state(self) -> Dict[str, Any]:
        """Get current file manager state"""
        return {
            'current_file_path': self.file_path_var.get(),
            'current_files': self.current_files.copy(),
            'current_file_index': self.current_file_index,
            'current_directory': self.current_directory,
            'recursive_enabled': self.recursive_enabled,
            'total_files': len(self.current_files),
            'has_navigation': len(self.current_files) > 1,
            'can_navigate_previous': self.current_file_index > 0,
            'can_navigate_next': self.current_file_index < len(self.current_files) - 1
        }
    
    def set_enabled(self, enabled: bool):
        """Enable/disable file manager components"""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        if self.file_path_var:
            # Enable/disable entry
            for widget in self._parent.winfo_children():
                if isinstance(widget, ttk.Entry):
                    widget.config(state=state)
        
        # Enable/disable buttons
        for widget in [self.prev_btn, self.next_btn]:
            if widget:
                widget.config(state=state)
    
    def load_file(self, file_path: str):
        """Load a single file"""
        if not file_path:
            return
        
        self.current_files = [file_path]
        self.current_file_index = 0
        self.current_directory = ""
        
        self.file_path_var.set(file_path)
        self._update_navigation_buttons()
        self._update_file_count_label()
        
        # Notify about file selection
        if self._event_bus:
            self._event_bus.publish(EventTypes.FILE_SELECTED, {
                'file_path': file_path,
                'file_index': 0,
                'total_files': 1
            })
    
    def load_files(self, files: List[str]):
        """Load multiple files"""
        if not files:
            return
        
        self.current_files = files.copy()
        self.current_file_index = 0
        self.current_directory = ""
        
        if files:
            self.file_path_var.set(files[0])
            self._update_navigation_buttons()
            self._update_file_count_label()
            
            # Notify about files loaded
            if self._event_bus:
                self._event_bus.publish(EventTypes.FILES_LOADED, {
                    'files': files,
                    'file_count': len(files)
                })
                
                # Select first file
                self._event_bus.publish(EventTypes.FILE_SELECTED, {
                    'file_path': files[0],
                    'file_index': 0,
                    'total_files': len(files)
                })
    
    def load_directory(self, directory_path: str):
        """Load directory and scan for files"""
        if not directory_path:
            return
        
        from core.file_manager import FileManager
        
        try:
            file_manager = FileManager(self.config)
            files = file_manager.select_directory(directory_path, self.recursive_enabled)
            
            if files:
                self.current_directory = directory_path
                self.load_files(files)
                
                # Show directory info
                recursive_text = "及其子目录" if self.recursive_enabled else ""
                status_msg = f"已加载 {len(files)} 个图片文件{recursive_text}"
                
                if self._event_bus:
                    self._event_bus.publish(EventTypes.CONFIG_CHANGED, {
                        'directory': directory_path,
                        'recursive': self.recursive_enabled,
                        'status_message': status_msg
                    })
            else:
                messagebox.showwarning("无图片文件", "所选文件夹中没有找到支持的图片文件")
                self.clear_all()
                
        except Exception as e:
            messagebox.showerror("加载失败", f"加载文件夹失败: {str(e)}")
            self.clear_all()
    
    def clear_all(self):
        """Clear all file selections"""
        self.current_files.clear()
        self.current_file_index = 0
        self.current_directory = ""
        self.file_path_var.set("")
        self._update_navigation_buttons()
        self._update_file_count_label()
    
    def _select_single_file(self):
        """Select single file dialog"""
        supported_formats = self.config.get_supported_formats()
        format_patterns = " ".join([f"*{fmt}" for fmt in supported_formats])
        
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", format_patterns),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.load_file(file_path)
    
    def _select_directory(self):
        """Select directory dialog"""
        directory_path = filedialog.askdirectory(title="选择包含图片的文件夹")
        
        if directory_path:
            self.load_directory(directory_path)
    
    def _on_recursive_change(self):
        """Handle recursive option change"""
        self.recursive_enabled = self.recursive_var.get()
        
        if self.recursive_enabled:
            self.recursive_hint_label.config(text="(勾选后读取文件夹及其所有子文件夹中的图片)")
        else:
            self.recursive_hint_label.config(text="(取消勾选后只读取当前文件夹中的图片)")
        
        # If directory is already selected, reload files
        if self.current_directory:
            self.load_directory(self.current_directory)
    
    def _show_previous_image(self):
        """Show previous image in navigation"""
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self._navigate_to_current_file()
    
    def _show_next_image(self):
        """Show next image in navigation"""
        if self.current_file_index < len(self.current_files) - 1:
            self.current_file_index += 1
            self._navigate_to_current_file()
    
    def _navigate_to_current_file(self):
        """Navigate to current file"""
        if self.current_files and 0 <= self.current_file_index < len(self.current_files):
            current_file = self.current_files[self.current_file_index]
            self.file_path_var.set(current_file)
            
            self._update_navigation_buttons()
            self._update_file_count_label()
            
            # Notify about navigation change
            if self._event_bus:
                self._event_bus.publish(EventTypes.NAVIGATION_CHANGED, {
                    'file_path': current_file,
                    'file_index': self.current_file_index,
                    'total_files': len(self.current_files)
                })
                
                # Select current file
                self._event_bus.publish(EventTypes.FILE_SELECTED, {
                    'file_path': current_file,
                    'file_index': self.current_file_index,
                    'total_files': len(self.current_files)
                })
    
    def _update_navigation_buttons(self):
        """Update navigation button states"""
        has_files = len(self.current_files) > 1
        has_prev = self.current_file_index > 0
        has_next = self.current_file_index < len(self.current_files) - 1
        
        self.prev_btn.config(state=tk.NORMAL if has_prev else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if has_next else tk.DISABLED)
    
    def _update_file_count_label(self):
        """Update file count label"""
        total_files = len(self.current_files)
        current_index = self.current_file_index + 1 if total_files > 0 else 0
        self.file_count_label.config(text=f"{current_index}/{total_files}")
    
    def get_current_file(self) -> Optional[str]:
        """Get current file path"""
        if self.current_files and 0 <= self.current_file_index < len(self.current_files):
            return self.current_files[self.current_file_index]
        return None
    
    def get_all_files(self) -> List[str]:
        """Get all loaded files"""
        return self.current_files.copy()
    
    def get_current_index(self) -> int:
        """Get current file index"""
        return self.current_file_index
    
    def set_current_index(self, index: int):
        """Set current file index"""
        if 0 <= index < len(self.current_files):
            self.current_file_index = index
            self._navigate_to_current_file()
    
    # Event handlers
    def _on_config_changed(self, event):
        """Handle config changed event"""
        if event.data and 'supported_formats' in event.data:
            # Supported formats changed, might need to reload current files
            if self.current_directory:
                self.load_directory(self.current_directory)
    
    def _on_navigation_next(self, event):
        """Handle navigation next event"""
        self._show_next_image()
    
    def _on_navigation_previous(self, event):
        """Handle navigation previous event"""
        self._show_previous_image()