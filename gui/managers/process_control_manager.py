"""
Process Control Manager for ImagePass GUI
Handles processing parameters and control operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, List

from architecture.interfaces import IUIComponent
from architecture.events import EventBus, EventTypes, subscribe_to
from architecture.di import inject
from processing.models import ProcessType, OutputMode
from core.config import Config
from processing.commands import ThreadedCommandExecutor, ProcessingCommandFactory
from processing.factory import ImageProcessorFactory


class ProcessControlManager(IUIComponent):
    """Manages processing controls and parameters"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._event_bus: Optional[EventBus] = None
        self._parent = None
        
        # UI components
        self.process_type_var = None
        self.params_frame = None
        self.param_input_frame = None
        self.output_mode_var = None
        self.process_btn = None
        self.stop_btn = None
        self.batch_process_btn = None
        self.select_output_btn = None
        
        # Parameter variables
        self.resize_mode_var = None
        self.percentage_var = None
        self.width_var = None
        self.height_var = None
        self.maintain_aspect_var = None
        self.tinypng_api_key_var = None
        self.api_key_status_label = None
        self.aspect_hint_label = None
        
        # State
        self.output_directory = None
        # Command executor
        self.command_executor = ThreadedCommandExecutor()
        self.processor_factory = ImageProcessorFactory(config)
        
    @inject('event_manager')
    def set_event_bus(self, event_bus: EventBus):
        """Set event bus for communication"""
        self._event_bus = event_bus
        
        # Subscribe to events
        event_bus.subscribe(EventTypes.FILE_SELECTED, self._on_file_selected)
        event_bus.subscribe(EventTypes.FILES_LOADED, self._on_files_loaded)
        event_bus.subscribe(EventTypes.PROCESSING_STARTED, self._on_processing_started)
        event_bus.subscribe(EventTypes.PROCESSING_COMPLETE, self._on_processing_complete)
        event_bus.subscribe(EventTypes.PROCESSING_ERROR, self._on_processing_error)
        event_bus.subscribe(EventTypes.PROCESSING_STOPPED, self._on_processing_stopped)
    
    def initialize(self, parent):
        """Initialize process control components"""
        self._parent = parent
        self._create_process_control_ui()
    
    def _create_process_control_ui(self):
        """Create process control user interface"""
        # Create control frame
        control_frame = ttk.LabelFrame(self._parent, text="处理控制", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Process type selection
        process_frame = ttk.Frame(control_frame)
        process_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(process_frame, text="处理方式:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.process_type_var = tk.StringVar(value=ProcessType.RESIZE.value)
        resize_radio = ttk.Radiobutton(process_frame, text="调整分辨率", 
                                      variable=self.process_type_var, value=ProcessType.RESIZE.value,
                                      command=self._on_process_type_change)
        resize_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        compress_radio = ttk.Radiobutton(process_frame, text="TinyPNG压缩", 
                                        variable=self.process_type_var, value=ProcessType.COMPRESS.value,
                                        command=self._on_process_type_change)
        compress_radio.pack(side=tk.LEFT)
        
        # Parameters frame
        self.params_frame = ttk.Frame(control_frame)
        self.params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create resize parameters by default
        self._create_resize_params()
        
        # Output options
        output_frame = ttk.Frame(control_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="输出方式:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.output_mode_var = tk.StringVar(value=OutputMode.NEW_FOLDER.value)
        overwrite_radio = ttk.Radiobutton(output_frame, text="覆盖原图", 
                                         variable=self.output_mode_var, value=OutputMode.OVERWRITE.value)
        overwrite_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        new_folder_radio = ttk.Radiobutton(output_frame, text="新建文件夹", 
                                          variable=self.output_mode_var, value=OutputMode.NEW_FOLDER.value)
        new_folder_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        custom_dir_radio = ttk.Radiobutton(output_frame, text="指定目录", 
                                          variable=self.output_mode_var, value=OutputMode.CUSTOM_DIR.value)
        custom_dir_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        self.select_output_btn = ttk.Button(output_frame, text="选择目录", 
                                          command=self._select_output_directory, 
                                          state=tk.DISABLED)
        self.select_output_btn.pack(side=tk.LEFT)
        
        # Bind output mode change
        self.output_mode_var.trace('w', self._on_output_mode_change)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.process_btn = ttk.Button(button_frame, text="处理图片", 
                                     command=self._on_process_clicked, state=tk.DISABLED)
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="停止处理", 
                                  command=self._on_stop_clicked, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        self.batch_process_btn = ttk.Button(button_frame, text="批量处理", 
                                           command=self._on_batch_process_clicked, state=tk.DISABLED)
        self.batch_process_btn.pack(side=tk.LEFT)
    
    def _create_resize_params(self):
        """Create resize parameter controls"""
        # Clear existing controls
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.params_frame, text="调整方式:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.resize_mode_var = tk.StringVar(value="percentage")
        percentage_radio = ttk.Radiobutton(self.params_frame, text="百分比", 
                                          variable=self.resize_mode_var, value="percentage",
                                          command=self._on_resize_mode_change)
        percentage_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        dimensions_radio = ttk.Radiobutton(self.params_frame, text="指定尺寸", 
                                          variable=self.resize_mode_var, value="dimensions",
                                          command=self._on_resize_mode_change)
        dimensions_radio.pack(side=tk.LEFT)
        
        # Parameter input frame
        self.param_input_frame = ttk.Frame(self.params_frame)
        self.param_input_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        # Create percentage input by default
        self._create_percentage_input()
    
    def _create_percentage_input(self):
        """Create percentage input controls"""
        for widget in self.param_input_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.param_input_frame, text="百分比:").pack(side=tk.LEFT)
        
        self.percentage_var = tk.StringVar(value="50")
        percentage_spinbox = ttk.Spinbox(self.param_input_frame, from_=1, to=200, 
                                       textvariable=self.percentage_var, width=10)
        percentage_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(self.param_input_frame, text="%").pack(side=tk.LEFT)
    
    def _create_dimensions_input(self):
        """Create dimensions input controls"""
        for widget in self.param_input_frame.winfo_children():
            widget.destroy()
        
        # Width and height input
        size_frame = ttk.Frame(self.param_input_frame)
        size_frame.pack(side=tk.TOP, pady=(0, 10))
        
        ttk.Label(size_frame, text="宽度:").pack(side=tk.LEFT)
        
        self.width_var = tk.StringVar(value="800")
        width_spinbox = ttk.Spinbox(size_frame, from_=1, to=5000, 
                                   textvariable=self.width_var, width=10)
        width_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(size_frame, text="高度:").pack(side=tk.LEFT)
        
        self.height_var = tk.StringVar(value="600")
        height_spinbox = ttk.Spinbox(size_frame, from_=1, to=5000, 
                                    textvariable=self.height_var, width=10)
        height_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # Aspect ratio option
        aspect_frame = ttk.Frame(self.param_input_frame)
        aspect_frame.pack(side=tk.TOP)
        
        self.maintain_aspect_var = tk.BooleanVar(value=True)
        aspect_check = ttk.Checkbutton(aspect_frame, text="保持宽高比", 
                                      variable=self.maintain_aspect_var,
                                      command=self._on_aspect_ratio_change)
        aspect_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Hint label
        self.aspect_hint_label = ttk.Label(aspect_frame, text="(保持比例，图片可能不完全匹配指定尺寸)", 
                                         foreground="gray", font=("Arial", 9))
        self.aspect_hint_label.pack(side=tk.LEFT)
    
    def _create_tinypng_params(self):
        """Create TinyPNG parameter controls"""
        # Clear existing controls
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        # API key input
        api_key_frame = ttk.Frame(self.params_frame)
        api_key_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(api_key_frame, text="API KEY:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Get current API key
        current_api_key = self.config.get_tinypng_api_key()
        default_api_key = "4PGdmZhdCHG9NJ53VMl2kTZfcFCFTTNH"
        api_key_value = current_api_key if current_api_key and current_api_key != 'your_tinypng_api_key_here' else default_api_key
        
        self.tinypng_api_key_var = tk.StringVar(value=api_key_value)
        api_key_entry = ttk.Entry(api_key_frame, textvariable=self.tinypng_api_key_var, width=40)
        api_key_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Save API key button
        save_api_key_btn = ttk.Button(api_key_frame, text="保存", command=self._save_tinypng_api_key)
        save_api_key_btn.pack(side=tk.LEFT)
        
        # API key status label
        self.api_key_status_label = ttk.Label(api_key_frame, text="", foreground="gray", font=("Arial", 9))
        self.api_key_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Update API key status
        self._update_api_key_status()
    
    def _update_api_key_status(self):
        """Update API key status display"""
        if not hasattr(self, 'tinypng_api_key_var'):
            return
        
        api_key = self.tinypng_api_key_var.get().strip()
        if api_key:
            if api_key == "4PGdmZhdCHG9NJ53VMl2kTZfcFCFTTNH":
                status_text = "(使用默认API密钥)"
                color = "green"
            else:
                status_text = "(自定义API密钥)"
                color = "blue"
        else:
            status_text = "(未设置API密钥)"
            color = "red"
        
        if hasattr(self, 'api_key_status_label'):
            self.api_key_status_label.config(text=status_text, foreground=color)
    
    def _save_tinypng_api_key(self):
        """Save TinyPNG API key"""
        if not hasattr(self, 'tinypng_api_key_var'):
            return
        
        api_key = self.tinypng_api_key_var.get().strip()
        
        if len(api_key) < 10:
            messagebox.showerror("API密钥错误", "API密钥长度不足，请检查输入")
            return
        
        try:
            # Save to config
            self.config.set_tinypng_api_key(api_key)
            self.config.save_config()
            
            # Notify about API key change
            if self._event_bus:
                self._event_bus.publish(EventTypes.CONFIG_CHANGED, {
                    'tinypng_api_key': api_key
                })
            
            messagebox.showinfo("保存成功", "API密钥已保存")
            self._update_api_key_status()
                
        except Exception as e:
            messagebox.showerror("保存失败", f"保存API密钥失败: {str(e)}")
    
    def _on_aspect_ratio_change(self):
        """Handle aspect ratio option change"""
        if self.maintain_aspect_var.get():
            self.aspect_hint_label.config(text="(保持比例，图片可能不完全匹配指定尺寸)")
        else:
            self.aspect_hint_label.config(text="(强制调整，图片将完全匹配指定尺寸，可能变形)")
    
    def update(self, data: Any):
        """Update process control with new data"""
        if isinstance(data, dict):
            if 'enabled' in data:
                self.set_enabled(data['enabled'])
            if 'processing' in data:
                self._set_processing_state(data['processing'])
    
    def get_state(self) -> Dict[str, Any]:
        """Get current process control state"""
        params = self._get_process_params()
        return {
            'process_type': self.process_type_var.get() if self.process_type_var else None,
            'output_mode': self.output_mode_var.get() if self.output_mode_var else None,
            'params': params,
            'output_directory': self.output_directory,
            'is_processing': self.is_processing,
            'can_process': self.process_btn['state'] == tk.NORMAL
        }
    
    def set_enabled(self, enabled: bool):
        """Enable/disable process control components"""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        if self.process_type_var:
            # Enable/disable radio buttons
            for widget in self.params_frame.winfo_children():
                if isinstance(widget, ttk.Radiobutton) or isinstance(widget, ttk.Button):
                    widget.config(state=state)
        
        if self.output_mode_var:
            # Enable/disable output mode controls
            for widget in self.params_frame.master.winfo_children():
                if isinstance(widget, ttk.Radiobutton) or isinstance(widget, ttk.Button):
                    widget.config(state=state)
        
        # Update process button based on current state
        if not self.is_processing:
            self.process_btn.config(state=state)
            self.batch_process_btn.config(state=state)
    
    def _set_processing_state(self, processing: bool):
        """Set processing state"""
        self.is_processing = processing
        
        if processing:
            self.process_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.batch_process_btn.config(state=tk.DISABLED)
        else:
            self.process_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.batch_process_btn.config(state=tk.NORMAL)
    
    @property
    def is_processing(self) -> bool:
        """Check if currently processing"""
        return hasattr(self, '_is_processing') and self._is_processing
    
    @is_processing.setter
    def is_processing(self, value: bool):
        """Set processing state"""
        self._is_processing = value
    
    def _get_process_params(self) -> Optional[Dict[str, Any]]:
        """Get current processing parameters"""
        process_type = self.process_type_var.get()
        
        if process_type == ProcessType.RESIZE.value:
            resize_mode = self.resize_mode_var.get()
            if resize_mode == "percentage":
                resize_value = int(self.percentage_var.get())
            else:
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                resize_value = (width, height)
            
            params = {
                'resize_mode': resize_mode,
                'resize_value': resize_value,
                'quality': 85
            }
            
            if resize_mode == "dimensions":
                params['maintain_aspect'] = self.maintain_aspect_var.get()
            
            return params
        elif process_type == ProcessType.COMPRESS.value:
            # Validate API key
            if hasattr(self, 'tinypng_api_key_var'):
                api_key = self.tinypng_api_key_var.get().strip()
                if not api_key:
                    messagebox.showerror("API密钥错误", "请先输入TinyPNG API密钥")
                    return None
            else:
                messagebox.showerror("API密钥错误", "请先输入TinyPNG API密钥")
                return None
            
            return {}
        else:
            return {}
    
    def _on_process_type_change(self):
        """Handle process type change"""
        process_type = self.process_type_var.get()
        if process_type == ProcessType.RESIZE.value:
            self._create_resize_params()
        elif process_type == ProcessType.COMPRESS.value:
            self._create_tinypng_params()
    
    def _on_resize_mode_change(self):
        """Handle resize mode change"""
        resize_mode = self.resize_mode_var.get()
        if resize_mode == "percentage":
            self._create_percentage_input()
        else:
            self._create_dimensions_input()
    
    def _on_output_mode_change(self, *args):
        """Handle output mode change"""
        output_mode = self.output_mode_var.get()
        if output_mode == OutputMode.CUSTOM_DIR.value:
            self.select_output_btn.config(state=tk.NORMAL)
        else:
            self.select_output_btn.config(state=tk.DISABLED)
    
    def _select_output_directory(self):
        """Select output directory"""
        from tkinter import filedialog
        
        directory_path = filedialog.askdirectory(title="选择输出目录")
        if directory_path:
            self.output_directory = directory_path
            
            if self._event_bus:
                self._event_bus.publish(EventTypes.CONFIG_CHANGED, {
                    'output_directory': directory_path
                })
    
    def _on_process_clicked(self):
        """Handle process button click"""
        if self.command_executor.is_processing():
            messagebox.showwarning("处理中", "请等待当前处理任务完成")
            return

        params = self._get_process_params()
        if params is None:
            return

        # Get current file from file manager
        # This is a temporary solution until the state is fully managed
        from gui.managers.file_manager_view import FileManagerView
        file_manager = self._parent.master.winfo_children()[0].winfo_children()[0]
        if isinstance(file_manager, FileManagerView):
            current_file = file_manager.get_current_file()
            if not current_file:
                messagebox.showerror("错误", "没有选中的文件")
                return

            # Generate output path
            output_path = self._get_output_path(current_file)

            strategy = self.processor_factory.get_strategy(self.process_type_var.get())
            command = ProcessingCommandFactory.create_single_command(
                strategy,
                current_file,
                output_path,
                params
            )
            self.command_executor.execute_command(command, self._on_processing_complete)

        if self._event_bus:
            self._event_bus.publish(EventTypes.PROCESSING_STARTED, {
                'type': 'single',
                'params': params,
                'output_mode': self.output_mode_var.get(),
                'output_directory': self.output_directory
            })
    
    def _get_output_path(self, input_path: str) -> str:
        """Generate output path based on output mode"""
        import os
        
        output_mode = self.output_mode_var.get()
        
        if output_mode == 'overwrite':
            return input_path
        elif output_mode == 'new_folder':
            # Create processed folder in same directory
            dir_name = os.path.dirname(input_path)
            base_name = os.path.basename(input_path)
            name, ext = os.path.splitext(base_name)
            processed_dir = os.path.join(dir_name, 'processed')
            
            # Create processed directory if it doesn't exist
            os.makedirs(processed_dir, exist_ok=True)
            
            return os.path.join(processed_dir, f"{name}_processed{ext}")
        elif output_mode == 'custom_dir' and self.output_directory:
            # Use custom directory
            base_name = os.path.basename(input_path)
            
            # Create custom directory if it doesn't exist
            os.makedirs(self.output_directory, exist_ok=True)
            
            return os.path.join(self.output_directory, base_name)
        else:
            # Fallback to same directory with suffix
            dir_name = os.path.dirname(input_path)
            base_name = os.path.basename(input_path)
            name, ext = os.path.splitext(base_name)
            return os.path.join(dir_name, f"{name}_processed{ext}")
    
    def _on_stop_clicked(self):
        """Handle stop button click"""
        if self._event_bus:
            self._event_bus.publish(EventTypes.PROCESSING_STOPPED)
    
    def _on_batch_process_clicked(self):
        """Handle batch process button click"""
        if self.command_executor.is_processing():
            messagebox.showwarning("处理中", "请等待当前处理任务完成")
            return

        params = self._get_process_params()
        if params is None:
            return

        # Get all files from file manager
        from gui.managers.file_manager_view import FileManagerView
        file_manager_view = self._parent.master.winfo_children()[0].winfo_children()[0]
        if isinstance(file_manager_view, FileManagerView):
            files = file_manager_view.get_all_files()
            if not files:
                messagebox.showerror("错误", "没有要处理的文件")
                return

            from processing.models import BatchProcessingOptions, ProcessingOptions
            options = ProcessingOptions(
                process_type=self.process_type_var.get(),
                output_mode=self.output_mode_var.get(),
                output_dir=self.output_directory,
                params=params
            )
            batch_options = BatchProcessingOptions(
                files=files,
                options=options
            )

            from core.file_manager import FileManager
            file_manager = FileManager(self.config)
            
            strategy = self.processor_factory.get_strategy(self.process_type_var.get())
            command = ProcessingCommandFactory.create_batch_command(
                strategy,
                file_manager,
                batch_options,
                self._on_batch_progress
            )
            self.command_executor.execute_command(command, self._on_batch_process_complete)

        if self._event_bus:
            self._event_bus.publish(EventTypes.PROCESSING_STARTED, {
                'type': 'batch',
                'params': params,
                'output_mode': self.output_mode_var.get(),
                'output_directory': self.output_directory
            })
    
    # Event handlers
    def _on_file_selected(self, event):
        """Handle file selected event"""
        if event.data and 'file_path' in event.data:
            self.process_btn.config(state=tk.NORMAL)

    def _on_files_loaded(self, event):
        """Handle files loaded event"""
        if event.data and 'file_count' in event.data:
            file_count = event.data['file_count']
            if file_count > 0:
                self.batch_process_btn.config(state=tk.NORMAL)
            else:
                self.batch_process_btn.config(state=tk.DISABLED)
    
    def _on_processing_started(self, event):
        """Handle processing started event"""
        self._set_processing_state(True)
    
    def _on_batch_progress(self, file_path, current, total):
        """Handle batch progress"""
        if self._event_bus:
            self._event_bus.publish(EventTypes.PROCESSING_PROGRESS, {
                'file_path': file_path,
                'current': current,
                'total': total
            })

    def _on_batch_process_complete(self, results):
        """Handle batch process complete"""
        # Reset processing state regardless of result
        self._set_processing_state(False)
        
        if self._event_bus:
            summary = f"批量处理完成! 成功: {len([r for r in results if r.success])}/{len(results)}"
            self._event_bus.publish(EventTypes.PROCESSING_COMPLETE, {
                'results': results,
                'summary': summary
            })

    def _on_processing_complete(self, results):
        """Handle single processing complete"""
        # Reset processing state regardless of result
        self._set_processing_state(False)
        
        if self._event_bus and results:
            result = results[0]
            if result.success:
                info_text = f"处理完成! 输入: {result.input_size//1024}KB, 输出: {result.output_size//1024}KB"
                if result.compression_ratio is not None:
                    info_text += f", 压缩率: {result.compression_ratio:.1f}%"
                self._event_bus.publish(EventTypes.PROCESSING_COMPLETE, {
                    'result': result,
                    'summary': info_text
                })
            else:
                self._event_bus.publish(EventTypes.PROCESSING_ERROR, {'error': result.error})

    
    def _on_processing_error(self, event):
        """Handle processing error event"""
        self._set_processing_state(False)
    
    def _on_processing_stopped(self, event):
        """Handle processing stopped event"""
        self._set_processing_state(False)