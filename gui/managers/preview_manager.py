"""
Preview Manager for ImagePass GUI
Handles image preview display and management
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from typing import Optional, Dict, Any

from architecture.interfaces import IUIComponent
from architecture.events import EventBus, EventTypes, subscribe_to
from architecture.di import inject
from core.config import Config


class PreviewManager(IUIComponent):
    """Manages image preview display"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._event_bus: Optional[EventBus] = None
        self._parent = None
        
        # UI components
        self.original_label = None
        self.processed_label = None
        self.original_resolution_label = None
        self.processed_resolution_label = None
        
        # Image references
        self.current_image_tk = None
        self.processed_image_tk = None
        
        # Current state
        self.current_image_path = ""
        self.processed_results = {}  # input_path -> output_path
        
        # Preview settings
        self.preview_size = self.config.get_preview_size()
        
    @inject('event_manager')
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for communication"""
        self._event_bus = event_bus
        
        # Subscribe to events
        event_bus.subscribe(EventTypes.FILE_SELECTED, self._on_file_selected)
        event_bus.subscribe(EventTypes.PROCESSING_COMPLETE, self._on_processing_complete)
        event_bus.subscribe(EventTypes.NAVIGATION_CHANGED, self._on_navigation_changed)
        event_bus.subscribe(EventTypes.CONFIG_CHANGED, self._on_config_changed)
    
    def initialize(self, parent):
        """Initialize preview components"""
        self._parent = parent
        self._create_preview_ui()
    
    def _create_preview_ui(self):
        """Create preview user interface"""
        # Create preview frame
        preview_frame = ttk.LabelFrame(self._parent, text="图片预览", padding="10")
        preview_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create preview container
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # Original image preview
        original_frame = ttk.LabelFrame(preview_container, text="原图", padding="5")
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.original_label = ttk.Label(original_frame, text="请选择图片文件", 
                                      relief=tk.SUNKEN, anchor=tk.CENTER)
        self.original_label.pack(fill=tk.BOTH, expand=True)
        
        self.original_resolution_label = ttk.Label(original_frame, text="", 
                                                 foreground="gray", font=("Arial", 9))
        self.original_resolution_label.pack(pady=(2, 0))
        
        # Processed image preview
        processed_frame = ttk.LabelFrame(preview_container, text="处理后", padding="5")
        processed_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.processed_label = ttk.Label(processed_frame, text="等待处理", 
                                        relief=tk.SUNKEN, anchor=tk.CENTER)
        self.processed_label.pack(fill=tk.BOTH, expand=True)
        
        self.processed_resolution_label = ttk.Label(processed_frame, text="", 
                                                  foreground="gray", font=("Arial", 9))
        self.processed_resolution_label.pack(pady=(2, 0))
        
        # Configure grid weights
        preview_container.columnconfigure(0, weight=1)
        preview_container.columnconfigure(1, weight=1)
    
    def update(self, data: Any):
        """Update preview with new data"""
        if isinstance(data, str):
            # Assume it's a file path
            self.load_image(data)
        elif isinstance(data, dict):
            if 'file_path' in data:
                self.load_image(data['file_path'])
            if 'processed_path' in data:
                self.load_processed_image(data['processed_path'])
    
    def get_state(self) -> Dict[str, Any]:
        """Get current preview state"""
        return {
            'current_image_path': self.current_image_path,
            'has_original_image': self.current_image_tk is not None,
            'has_processed_image': self.processed_image_tk is not None,
            'processed_results': self.processed_results.copy()
        }
    
    def set_enabled(self, enabled: bool):
        """Enable/disable preview components"""
        state = tk.NORMAL if enabled else tk.DISABLED
        if self.original_label:
            self.original_label.config(state=state)
        if self.processed_label:
            self.processed_label.config(state=state)
    
    def load_image(self, image_path: str):
        """Load and display an image"""
        if not os.path.exists(image_path):
            self._show_error("文件不存在", self.original_label)
            return
        
        self.current_image_path = image_path
        
        try:
            # Display original image
            self.display_image(image_path, self.original_label, is_original=True)
            
            # Check for processed result
            if image_path in self.processed_results:
                processed_path = self.processed_results[image_path]
                if os.path.exists(processed_path):
                    self.display_image(processed_path, self.processed_label, is_original=False)
                else:
                    self._clear_processed_preview()
                    # Remove invalid result from cache
                    del self.processed_results[image_path]
            else:
                self._clear_processed_preview()
            
            # Notify about image load
            if self._event_bus:
                self._event_bus.publish(EventTypes.PREVIEW_UPDATED, {
                    'file_path': image_path,
                    'loaded': True
                })
                
        except Exception as e:
            self._show_error(f"加载失败: {str(e)}", self.original_label)
            self._clear_processed_preview()
    
    def load_processed_image(self, processed_path: str):
        """Load and display processed image"""
        if not os.path.exists(processed_path):
            self._show_error("处理结果文件不存在", self.processed_label)
            return
        
        try:
            self.display_image(processed_path, self.processed_label, is_original=False)
            
            # Cache the result
            if self.current_image_path:
                self.processed_results[self.current_image_path] = processed_path
            
        except Exception as e:
            self._show_error(f"加载处理结果失败: {str(e)}", self.processed_label)
    
    def display_image(self, image_path: str, label_widget: ttk.Label, is_original: bool = True):
        """Display image in specified label widget"""
        try:
            # Open image
            pil_image = Image.open(image_path)
            
            # Get widget size for scaling
            label_widget.update_idletasks()
            label_width = label_widget.winfo_width()
            label_height = label_widget.winfo_height()
            
            # Calculate scaling
            max_width, max_height = self.preview_size
            if label_width > 1 and label_height > 1:
                max_width = min(max_width, label_width - 10)
                max_height = min(max_height, label_height - 10)
            
            # Resize image
            pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convert to Tkinter format
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # Display image
            label_widget.config(image=tk_image, text="")
            
            # Store reference to prevent garbage collection
            if is_original:
                self.current_image_tk = tk_image
            else:
                self.processed_image_tk = tk_image
            
            # Update image info
            info_text = self._get_image_info_text(image_path)
            if is_original:
                self.original_resolution_label.config(text=info_text)
            else:
                self.processed_resolution_label.config(text=info_text)
                
        except Exception as e:
            self._show_error(f"显示错误: {str(e)}", label_widget)
            # Clear info display
            if is_original:
                self.original_resolution_label.config(text="")
            else:
                self.processed_resolution_label.config(text="")
    
    def _clear_original_preview(self):
        """Clear original image preview"""
        if self.original_label:
            self.original_label.config(image='', text="请选择图片文件")
        self.original_resolution_label.config(text="")
        self.current_image_tk = None
        self.current_image_path = ""
    
    def _clear_processed_preview(self):
        """Clear processed image preview"""
        if self.processed_label:
            self.processed_label.config(image='', text="等待处理")
        self.processed_resolution_label.config(text="")
        self.processed_image_tk = None
    
    def _show_error(self, message: str, label_widget: ttk.Label):
        """Show error message in label widget"""
        if label_widget:
            label_widget.config(image='', text=message)
    
    def _get_image_info_text(self, image_path: str) -> str:
        """Get formatted image information text"""
        try:
            # Get file size
            if os.path.exists(image_path):
                size_bytes = os.path.getsize(image_path)
                if size_bytes < 1024:
                    file_size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    file_size = f"{size_bytes // 1024} KB"
                else:
                    file_size = f"{size_bytes // (1024 * 1024):.1f} MB"
            else:
                file_size = "未知大小"
            
            # Get image dimensions
            try:
                with Image.open(image_path) as img:
                    resolution = f"{img.width} × {img.height}"
            except Exception:
                resolution = "未知分辨率"
            
            return f"{resolution} | {file_size}"
            
        except Exception:
            return "信息获取失败"
    
    def clear_all(self):
        """Clear all preview displays"""
        self._clear_original_preview()
        self._clear_processed_preview()
        self.processed_results.clear()
    
    def update_preview_size(self):
        """Update preview size from config"""
        self.preview_size = self.config.get_preview_size()
        # Reload current image if any
        if self.current_image_path and os.path.exists(self.current_image_path):
            self.load_image(self.current_image_path)
    
    # Event handlers
    def _on_file_selected(self, event):
        """Handle file selected event"""
        if event.data and 'file_path' in event.data:
            self.processed_results.clear()  # Clear cache for new file
            self.load_image(event.data['file_path'])
    
    def _on_processing_complete(self, event):
        """Handle processing complete event"""
        if event.data and 'result' in event.data:
            result = event.data['result']
            if result.get('success') and result.get('output_path'):
                self.load_processed_image(result['output_path'])
    
    def _on_navigation_changed(self, event):
        """Handle navigation changed event"""
        if event.data and 'file_path' in event.data:
            self.load_image(event.data['file_path'])
    
    def _on_config_changed(self, event):
        """Handle config changed event"""
        if event.data and 'preview_size' in event.data:
            self.update_preview_size()