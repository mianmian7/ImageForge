"""
处理控制管理器模块
管理图像处理控制和参数设置
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from typing import Optional, Callable, Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


class ProcessControlManager:
    """处理控制管理器类"""
    
    def __init__(self, parent: tk.Widget, config, processor, file_manager):
        """初始化处理控制管理器"""
        self.parent = parent
        self.config = config
        self.processor = processor
        self.file_manager = file_manager
        
        # 回调函数
        self.on_process_complete_callback = None
        self.on_process_error_callback = None
        self.on_batch_progress_callback = None
        self.on_batch_complete_callback = None
        
        # UI 组件
        self.control_frame = None
        self.process_type_var = None
        self.resize_mode_var = None
        self.percentage_var = None
        self.width_var = None
        self.height_var = None
        self.maintain_aspect_var = None
        self.output_mode_var = None
        self.output_format_var = None
        self.meta_override_var = None
        self.tinypng_api_key_var = None
        self.pillow_quality_var = None
        self.pillow_mode_var = None
        self.pillow_scale_var = None
        
        # UI子组件
        self.params_frame = None
        self.param_input_frame = None
        self.aspect_hint_label = None
        self.api_key_status_label = None
        self.pillow_quality_hint_label = None
        self.pillow_resize_frame = None
        self.select_output_btn = None
        self.process_btn = None
        self.stop_btn = None
        self.batch_process_btn = None
        
        # 状态
        self.is_processing = False
        self.processing_thread = None
        self.output_directory = None
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """创建处理控制组件"""
        self.control_frame = ttk.LabelFrame(self.parent, text="处理控制", padding="10")
        
        # 处理方式选择
        self._create_process_type_selection()
        
        # 参数设置区域
        self.params_frame = ttk.Frame(self.control_frame)
        self.params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 初始化为调整分辨率参数
        self.create_resize_params()
        
        # 输出选项
        self._create_output_options()
        
        # 处理按钮
        self._create_processing_buttons()
    
    def _create_process_type_selection(self):
        """创建处理方式选择"""
        process_frame = ttk.Frame(self.control_frame)
        process_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(process_frame, text="处理方式:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.process_type_var = tk.StringVar(value="resize")
        resize_radio = ttk.Radiobutton(process_frame, text="调整分辨率", 
                                      variable=self.process_type_var, value="resize",
                                      command=self.on_process_type_change)
        resize_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        compress_radio = ttk.Radiobutton(process_frame, text="TinyPNG压缩", 
                                        variable=self.process_type_var, value="compress",
                                        command=self.on_process_type_change)
        compress_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        pillow_compress_radio = ttk.Radiobutton(process_frame, text="Pillow压缩", 
                                              variable=self.process_type_var, value="pillow_compress",
                                              command=self.on_process_type_change)
        pillow_compress_radio.pack(side=tk.LEFT)
    
    def _create_output_options(self):
        """创建输出选项"""
        output_frame = ttk.Frame(self.control_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="输出方式:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.output_mode_var = tk.StringVar(value="new_folder")
        overwrite_radio = ttk.Radiobutton(output_frame, text="覆盖原图", 
                                         variable=self.output_mode_var, value="overwrite")
        overwrite_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        new_folder_radio = ttk.Radiobutton(output_frame, text="新建文件夹", 
                                          variable=self.output_mode_var, value="new_folder")
        new_folder_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        custom_dir_radio = ttk.Radiobutton(output_frame, text="指定目录", 
                                          variable=self.output_mode_var, value="custom_dir")
        custom_dir_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        self.select_output_btn = ttk.Button(output_frame, text="选择目录", 
                                          command=self._select_output_directory, state=tk.DISABLED)
        self.select_output_btn.pack(side=tk.LEFT)
        
        self.output_mode_var.trace('w', self._on_output_mode_change)
    
    def _create_processing_buttons(self):
        """创建处理按钮"""
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X)
        
        self.process_btn = ttk.Button(button_frame, text="处理图片",
                                     command=lambda: self.process_image(), state=tk.DISABLED)
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(button_frame, text="停止处理",
                                  command=lambda: self.stop_processing(), state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.batch_process_btn = ttk.Button(button_frame, text="批量处理",
                                           command=lambda: self.batch_process_images(), state=tk.DISABLED)
        self.batch_process_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 输出格式选择
        ttk.Label(button_frame, text="输出格式:").pack(side=tk.LEFT, padx=(10, 5))
        
        self.output_format_var = tk.StringVar(value="保持原格式")
        format_combo = ttk.Combobox(button_frame, textvariable=self.output_format_var, 
                                   values=["保持原格式", "JPEG", "PNG", "WEBP", "BMP", "TIFF"], 
                                   width=12, state="readonly")
        format_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Meta覆盖选项
        self.meta_override_var = tk.BooleanVar(value=False)
        meta_override_checkbox = ttk.Checkbutton(button_frame, text="Meta覆盖", 
                                               variable=self.meta_override_var)
        meta_override_checkbox.pack(side=tk.LEFT, padx=(10, 0))
    
    def _setup_layout(self):
        """设置组件布局"""
        pass
    
    def create_resize_params(self):
        """创建分辨率调整参数控件"""
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
        
        self.param_input_frame = ttk.Frame(self.params_frame)
        self.param_input_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        self._on_resize_mode_change()
    
    def _create_percentage_input(self):
        """创建百分比输入控件"""
        for widget in self.param_input_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.param_input_frame, text="百分比:").pack(side=tk.LEFT)
        
        self.percentage_var = tk.StringVar(value="50")
        percentage_spinbox = ttk.Spinbox(self.param_input_frame, from_=1, to=200, 
                                       textvariable=self.percentage_var, width=10)
        percentage_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(self.param_input_frame, text="%").pack(side=tk.LEFT)
    
    def _create_dimensions_input(self):
        """创建尺寸输入控件"""
        for widget in self.param_input_frame.winfo_children():
            widget.destroy()
        
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
        
        aspect_frame = ttk.Frame(self.param_input_frame)
        aspect_frame.pack(side=tk.TOP)
        
        self.maintain_aspect_var = tk.BooleanVar(value=True)
        aspect_check = ttk.Checkbutton(aspect_frame, text="保持宽高比", 
                                      variable=self.maintain_aspect_var,
                                      command=self._on_aspect_ratio_change)
        aspect_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.aspect_hint_label = ttk.Label(aspect_frame, text="(保持比例，图片可能不完全匹配指定尺寸)", 
                                         foreground="gray", font=("Arial", 9))
        self.aspect_hint_label.pack(side=tk.LEFT)
    
    def create_tinypng_params(self):
        """创建TinyPNG压缩参数控件"""
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        api_key_frame = ttk.Frame(self.params_frame)
        api_key_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(api_key_frame, text="API KEY:").pack(side=tk.LEFT, padx=(0, 5))
        
        current_api_key = self.config.get_tinypng_api_key()
        default_api_key = "4PGdmZhdCHG9NJ53VMl2kTZfcFCFTTNH"
        api_key_value = current_api_key if current_api_key and current_api_key != 'your_tinypng_api_key_here' else default_api_key
        
        self.tinypng_api_key_var = tk.StringVar(value=api_key_value)
        api_key_entry = ttk.Entry(api_key_frame, textvariable=self.tinypng_api_key_var, width=40)
        api_key_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        save_api_key_btn = ttk.Button(api_key_frame, text="保存", command=self._save_tinypng_api_key)
        save_api_key_btn.pack(side=tk.LEFT)
        
        self.api_key_status_label = ttk.Label(api_key_frame, text="", foreground="gray", font=("Arial", 9))
        self.api_key_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self._update_api_key_status()
    
    def create_pillow_compress_params(self):
        """创建Pillow压缩参数控件"""
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        quality_frame = ttk.Frame(self.params_frame)
        quality_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(quality_frame, text="压缩质量:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.pillow_quality_var = tk.StringVar(value="85")
        quality_spinbox = ttk.Spinbox(quality_frame, from_=1, to=100, 
                                    textvariable=self.pillow_quality_var, width=10)
        quality_spinbox.pack(side=tk.LEFT, padx=(5, 5))
        
        self.pillow_quality_hint_label = ttk.Label(quality_frame, text="(1-100, 数值越小压缩率越高)", 
                                                  foreground="gray", font=("Arial", 9))
        self.pillow_quality_hint_label.pack(side=tk.LEFT)
        
        self.pillow_quality_var.trace('w', self._on_pillow_quality_change)
        
        mode_frame = ttk.Frame(self.params_frame)
        mode_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(mode_frame, text="压缩模式:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.pillow_mode_var = tk.StringVar(value="optimize")
        optimize_radio = ttk.Radiobutton(mode_frame, text="优化质量", 
                                       variable=self.pillow_mode_var, value="optimize")
        optimize_radio.pack(side=tk.LEFT, padx=(0, 5))
        
        resize_radio = ttk.Radiobutton(mode_frame, text="缩放压缩", 
                                     variable=self.pillow_mode_var, value="resize_optimize")
        resize_radio.pack(side=tk.LEFT)
        
        self.pillow_resize_frame = ttk.Frame(self.params_frame)
        self.pillow_resize_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Label(self.pillow_resize_frame, text="缩放比例:").pack(side=tk.LEFT)
        
        self.pillow_scale_var = tk.StringVar(value="80")
        scale_spinbox = ttk.Spinbox(self.pillow_resize_frame, from_=10, to=100, 
                                  textvariable=self.pillow_scale_var, width=10)
        scale_spinbox.pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Label(self.pillow_resize_frame, text="%").pack(side=tk.LEFT)
        
        self.pillow_mode_var.trace('w', self._on_pillow_mode_change)
        
        self._on_pillow_mode_change()
        self._on_pillow_quality_change()
    
    def on_process_type_change(self):
        """处理方式变化时的处理"""
        process_type = self.process_type_var.get()
        if process_type == "resize":
            self.create_resize_params()
        elif process_type == "compress":
            self.create_tinypng_params()
        elif process_type == "pillow_compress":
            self.create_pillow_compress_params()
    
    def _on_resize_mode_change(self):
        """调整方式变化时的处理"""
        resize_mode = self.resize_mode_var.get()
        if resize_mode == "percentage":
            self._create_percentage_input()
        else:
            self._create_dimensions_input()
    
    def _on_aspect_ratio_change(self):
        """处理宽高比选项变更"""
        if self.maintain_aspect_var.get():
            self.aspect_hint_label.config(text="(保持比例，图片可能不完全匹配指定尺寸)")
        else:
            self.aspect_hint_label.config(text="(强制调整，图片将完全匹配指定尺寸，可能变形)")
    
    def _on_output_mode_change(self, *args):
        """输出方式变化时的处理"""
        output_mode = self.output_mode_var.get()
        if output_mode == "custom_dir":
            self.select_output_btn.config(state=tk.NORMAL)
        else:
            self.select_output_btn.config(state=tk.DISABLED)
    
    def _select_output_directory(self):
        """选择输出目录"""
        directory_path = filedialog.askdirectory(title="选择输出目录")
        if directory_path:
            self.output_directory = directory_path
            logger.info(f"输出目录已设置: {directory_path}")
    
    def _on_pillow_mode_change(self, *args):
        """处理Pillow压缩模式变化"""
        if hasattr(self, 'pillow_mode_var') and hasattr(self, 'pillow_resize_frame'):
            if self.pillow_mode_var.get() == "resize_optimize":
                self.pillow_resize_frame.pack(side=tk.LEFT, padx=(20, 0))
            else:
                self.pillow_resize_frame.pack_forget()
    
    def _on_pillow_quality_change(self, *args):
        """处理Pillow压缩质量变化"""
        if hasattr(self, 'pillow_quality_var') and hasattr(self, 'pillow_quality_hint_label'):
            try:
                quality = int(self.pillow_quality_var.get())
                if quality <= 10:
                    hint_text, color = "(极限压缩: 极小文件，严重失真)", "red"
                elif quality <= 30:
                    hint_text, color = "(高压缩: 小文件，明显失真)", "orange"
                elif quality <= 50:
                    hint_text, color = "(中等压缩: 较小文件，轻微失真)", "blue"
                elif quality <= 75:
                    hint_text, color = "(轻度压缩: 轻微减小，质量良好)", "green"
                else:
                    hint_text, color = "(高质量: 文件较大，质量优秀)", "darkgreen"
                
                self.pillow_quality_hint_label.config(text=f"({quality}/100 {hint_text[1:]})", foreground=color)
            except ValueError:
                self.pillow_quality_hint_label.config(text="(1-100, 数值越小压缩率越高)", foreground="gray")
    
    def _save_tinypng_api_key(self):
        """保存TinyPNG API密钥"""
        if not hasattr(self, 'tinypng_api_key_var'):
            return
        
        api_key = self.tinypng_api_key_var.get().strip()
        
        if len(api_key) < 10:
            messagebox.showerror("API密钥错误", "API密钥长度不足，请检查输入")
            return
        
        try:
            self.config.set_tinypng_api_key(api_key)
            self.config.save_config()
            self.processor.set_tinypng_api_key(api_key)
            
            if self.processor.validate_tinypng_api_key(api_key):
                messagebox.showinfo("保存成功", "API密钥保存成功且验证通过")
                self.api_key_status_label.config(text="(API密钥有效)", foreground="green")
            else:
                messagebox.showwarning("保存成功", "API密钥已保存，但验证失败，请检查网络连接或密钥正确性")
                self.api_key_status_label.config(text="(API密钥验证失败)", foreground="orange")
                
        except Exception as e:
            messagebox.showerror("保存失败", f"保存API密钥失败: {str(e)}")
    
    def _update_api_key_status(self):
        """更新API密钥状态"""
        api_key = self.tinypng_api_key_var.get() if hasattr(self, 'tinypng_api_key_var') else ''
        if api_key:
            if api_key == "4PGdmZhdCHG9NJ53VMl2kTZfcFCFTTNH":
                status_text, color = "(使用默认API密钥)", "green"
            else:
                status_text, color = "(自定义API密钥)", "blue"
        else:
            status_text, color = "(未设置API密钥)", "red"
        
        if hasattr(self, 'api_key_status_label'):
            self.api_key_status_label.config(text=status_text, foreground=color)
    
    def get_process_params(self) -> Optional[Dict[str, Any]]:
        """获取处理参数"""
        process_type = self.process_type_var.get()
        
        if process_type == "resize":
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
            
        elif process_type == "compress":
            if hasattr(self, 'tinypng_api_key_var'):
                api_key = self.tinypng_api_key_var.get().strip()
                if api_key:
                    self.processor.set_tinypng_api_key(api_key)
                    params = {}
                else:
                    messagebox.showerror("API密钥错误", "请先输入TinyPNG API密钥")
                    return None
            else:
                messagebox.showerror("API密钥错误", "请先输入TinyPNG API密钥")
                return None
        elif process_type == "pillow_compress":
            if hasattr(self, 'pillow_quality_var') and hasattr(self, 'pillow_mode_var'):
                params = {
                    'quality': int(self.pillow_quality_var.get()),
                    'mode': self.pillow_mode_var.get()
                }
                
                if self.pillow_mode_var.get() == "resize_optimize" and hasattr(self, 'pillow_scale_var'):
                    params['scale'] = int(self.pillow_scale_var.get())
            else:
                messagebox.showerror("参数错误", "Pillow压缩参数设置错误")
                return None
        else:
            params = {}
        
        if not 'params' in locals():
            params = {}
        
        if hasattr(self, 'output_format_var'):
            output_format = self.output_format_var.get()
            if output_format != "保持原格式":
                params['output_format'] = output_format
                if output_format in ["JPEG", "WEBP"] and 'quality' not in params:
                    params['quality'] = 85
        
        if hasattr(self, 'meta_override_var'):
            params['meta_override'] = self.meta_override_var.get()
        
        return params
    
    def process_image(self):
        """处理当前图片（占位方法，由主窗口连接）"""
        pass
    
    def batch_process_images(self):
        """批量处理图片（占位方法，由主窗口连接）"""
        pass
    
    def stop_processing(self):
        """停止处理"""
        self.processor.stop_all_processing()
        logger.info("正在停止处理...")
    
    def set_processing_state(self, is_processing: bool):
        """设置处理状态"""
        self.is_processing = is_processing
        if is_processing:
            self.process_btn.config(state=tk.DISABLED)
            self.batch_process_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.process_btn.config(state=tk.NORMAL)
            self.batch_process_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def enable_processing(self, enable: bool = True):
        """启用/禁用处理按钮"""
        state = tk.NORMAL if enable else tk.DISABLED
        self.process_btn.config(state=state)
    
    def enable_batch_processing(self, enable: bool = True):
        """启用/禁用批量处理按钮"""
        state = tk.NORMAL if enable else tk.DISABLED
        self.batch_process_btn.config(state=state)
    
    def set_callbacks(self, on_process_complete: Callable = None,
                     on_process_error: Callable = None,
                     on_batch_progress: Callable = None,
                     on_batch_complete: Callable = None):
        """设置回调函数"""
        self.on_process_complete_callback = on_process_complete
        self.on_process_error_callback = on_process_error
        self.on_batch_progress_callback = on_batch_progress
        self.on_batch_complete_callback = on_batch_complete
    
    def get_output_mode(self) -> str:
        """获取输出模式"""
        return self.output_mode_var.get()
    
    def get_output_directory(self) -> Optional[str]:
        """获取输出目录"""
        return self.output_directory
    
    def get_process_type(self) -> str:
        """获取处理类型"""
        return self.process_type_var.get()
    
    def grid(self, **kwargs):
        """放置处理控制区域到指定位置"""
        self.control_frame.grid(**kwargs)