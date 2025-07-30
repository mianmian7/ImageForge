"""
主窗口GUI模块
提供主要的用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
from typing import Optional, List, Dict, Any

from core.image_processor import ImageProcessor
from core.file_manager import FileManager

class ImageProcessorGUI:
    """图像处理器主窗口类"""
    
    def __init__(self, root, config):
        """初始化主窗口
        
        Args:
            root: Tk根窗口
            config: 配置管理器
        """
        self.root = root
        self.config = config
        self.processor = ImageProcessor(config)
        self.file_manager = FileManager(config)
        
        # 当前文件相关
        self.current_image_path = ""
        self.current_image_tk = None
        self.processed_image_tk = None
        
        # 处理相关
        self.processing_thread = None
        self.is_processing = False
        
        # 设置窗口图标和标题
        self.root.title("ImagePass - 图像处理器")
        self.setup_ui()
        self.bind_events()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 文件选择区域
        self.create_file_selection_area(main_frame)
        
        # 图片预览区域
        self.create_preview_area(main_frame)
        
        # 控制面板区域
        self.create_control_panel(main_frame)
        
        # 状态栏
        self.create_status_bar(main_frame)
    
    def create_file_selection_area(self, parent):
        """创建文件选择区域"""
        file_frame = ttk.LabelFrame(parent, text="文件选择", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 文件路径显示
        self.file_path_var = tk.StringVar()
        file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        file_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 选择文件按钮
        select_file_btn = ttk.Button(file_frame, text="选择文件", command=self.select_single_file)
        select_file_btn.grid(row=0, column=1, padx=(0, 5))
        
        # 选择文件夹按钮
        select_folder_btn = ttk.Button(file_frame, text="选择文件夹", command=self.select_directory)
        select_folder_btn.grid(row=0, column=2, padx=(0, 5))
        
        # 文件导航按钮
        self.prev_btn = ttk.Button(file_frame, text="上一张", command=self.show_previous_image, state=tk.DISABLED)
        self.prev_btn.grid(row=0, column=3, padx=(0, 5))
        
        self.next_btn = ttk.Button(file_frame, text="下一张", command=self.show_next_image, state=tk.DISABLED)
        self.next_btn.grid(row=0, column=4)
        
        # 文件计数标签
        self.file_count_label = ttk.Label(file_frame, text="0/0")
        self.file_count_label.grid(row=0, column=5, padx=(10, 0))
        
        file_frame.columnconfigure(0, weight=1)
    
    def create_preview_area(self, parent):
        """创建图片预览区域"""
        preview_frame = ttk.LabelFrame(parent, text="图片预览", padding="10")
        preview_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 预览容器
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # 原图预览
        original_frame = ttk.LabelFrame(preview_container, text="原图", padding="5")
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.original_label = ttk.Label(original_frame, text="请选择图片文件", 
                                      relief=tk.SUNKEN, anchor=tk.CENTER)
        self.original_label.pack(fill=tk.BOTH, expand=True)
        
        # 处理后预览
        processed_frame = ttk.LabelFrame(preview_container, text="处理后", padding="5")
        processed_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.processed_label = ttk.Label(processed_frame, text="等待处理", 
                                        relief=tk.SUNKEN, anchor=tk.CENTER)
        self.processed_label.pack(fill=tk.BOTH, expand=True)
        
        preview_container.columnconfigure(0, weight=1)
        preview_container.columnconfigure(1, weight=1)
    
    def create_control_panel(self, parent):
        """创建控制面板区域"""
        control_frame = ttk.LabelFrame(parent, text="处理控制", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 处理方式选择
        process_frame = ttk.Frame(control_frame)
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
        compress_radio.pack(side=tk.LEFT)
        
        # 参数设置区域
        self.params_frame = ttk.Frame(control_frame)
        self.params_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_resize_params()
        
        # 输出选项
        output_frame = ttk.Frame(control_frame)
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
                                          command=self.select_output_directory, 
                                          state=tk.DISABLED)
        self.select_output_btn.pack(side=tk.LEFT)
        
        # 处理按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.process_btn = ttk.Button(button_frame, text="处理图片", 
                                     command=self.process_image, state=tk.DISABLED)
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="停止处理", 
                                  command=self.stop_processing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        self.batch_process_btn = ttk.Button(button_frame, text="批量处理", 
                                           command=self.batch_process_images, state=tk.DISABLED)
        self.batch_process_btn.pack(side=tk.LEFT)
    
    def create_resize_params(self):
        """创建分辨率调整参数控件"""
        # 清空现有控件
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.params_frame, text="调整方式:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.resize_mode_var = tk.StringVar(value="percentage")
        percentage_radio = ttk.Radiobutton(self.params_frame, text="百分比", 
                                          variable=self.resize_mode_var, value="percentage",
                                          command=self.on_resize_mode_change)
        percentage_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        dimensions_radio = ttk.Radiobutton(self.params_frame, text="指定尺寸", 
                                          variable=self.resize_mode_var, value="dimensions",
                                          command=self.on_resize_mode_change)
        dimensions_radio.pack(side=tk.LEFT)
        
        # 参数输入区域
        self.param_input_frame = ttk.Frame(self.params_frame)
        self.param_input_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        self.on_resize_mode_change()
    
    def create_percentage_input(self):
        """创建百分比输入控件"""
        for widget in self.param_input_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.param_input_frame, text="百分比:").pack(side=tk.LEFT)
        
        self.percentage_var = tk.StringVar(value="50")
        percentage_spinbox = ttk.Spinbox(self.param_input_frame, from_=1, to=200, 
                                       textvariable=self.percentage_var, width=10)
        percentage_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(self.param_input_frame, text="%").pack(side=tk.LEFT)
    
    def create_dimensions_input(self):
        """创建尺寸输入控件"""
        for widget in self.param_input_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.param_input_frame, text="宽度:").pack(side=tk.LEFT)
        
        self.width_var = tk.StringVar(value="800")
        width_spinbox = ttk.Spinbox(self.param_input_frame, from_=1, to=5000, 
                                   textvariable=self.width_var, width=10)
        width_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(self.param_input_frame, text="高度:").pack(side=tk.LEFT)
        
        self.height_var = tk.StringVar(value="600")
        height_spinbox = ttk.Spinbox(self.param_input_frame, from_=1, to=5000, 
                                    textvariable=self.height_var, width=10)
        height_spinbox.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="就绪", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
    
    def bind_events(self):
        """绑定事件处理"""
        # 输出模式变化
        self.output_mode_var.trace('w', self.on_output_mode_change)
    
    def select_single_file(self):
        """选择单个文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.load_image(file_path)
    
    def select_directory(self):
        """选择文件夹"""
        directory_path = filedialog.askdirectory(title="选择包含图片的文件夹")
        
        if directory_path:
            files = self.file_manager.select_directory(directory_path)
            if files:
                self.load_image(files[0])
                self.update_navigation_buttons()
                self.update_file_count_label()
                self.batch_process_btn.config(state=tk.NORMAL)
                self.status_label.config(text=f"已加载 {len(files)} 个图片文件")
            else:
                messagebox.showwarning("无图片文件", "所选文件夹中没有找到支持的图片文件")
    
    def load_image(self, image_path):
        """加载图片"""
        try:
            self.current_image_path = image_path
            self.file_path_var.set(image_path)
            
            # 显示原图
            self.display_image(image_path, self.original_label)
            
            # 清空处理后预览
            self.processed_label.config(image='', text="等待处理")
            self.processed_image_tk = None
            
            # 启用处理按钮
            self.process_btn.config(state=tk.NORMAL)
            
            # 更新状态
            self.status_label.config(text=f"已加载: {os.path.basename(image_path)}")
            
        except Exception as e:
            messagebox.showerror("加载失败", f"无法加载图片: {str(e)}")
    
    def display_image(self, image_path, label_widget):
        """在指定标签中显示图片"""
        try:
            # 打开图片
            pil_image = Image.open(image_path)
            
            # 获取标签大小
            label_widget.update_idletasks()
            label_width = label_widget.winfo_width()
            label_height = label_widget.winfo_height()
            
            # 计算缩放比例
            max_width, max_height = self.config.get_preview_size()
            if label_width > 1 and label_height > 1:
                max_width = min(max_width, label_width - 10)
                max_height = min(max_height, label_height - 10)
            
            # 调整图片大小
            pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # 转换为Tkinter格式
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # 显示图片
            label_widget.config(image=tk_image, text="")
            
            # 保存引用防止被垃圾回收
            if label_widget == self.original_label:
                self.current_image_tk = tk_image
            else:
                self.processed_image_tk = tk_image
                
        except Exception as e:
            label_widget.config(image='', text=f"显示错误: {str(e)}")
    
    def show_previous_image(self):
        """显示上一张图片"""
        prev_file = self.file_manager.get_previous_file()
        if prev_file:
            self.load_image(prev_file)
            self.update_file_count_label()
    
    def show_next_image(self):
        """显示下一张图片"""
        next_file = self.file_manager.get_next_file()
        if next_file:
            self.load_image(next_file)
            self.update_file_count_label()
    
    def update_navigation_buttons(self):
        """更新导航按钮状态"""
        file_count = self.file_manager.get_file_count()
        if file_count > 1:
            self.prev_btn.config(state=tk.NORMAL)
            self.next_btn.config(state=tk.NORMAL)
        else:
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
    
    def update_file_count_label(self):
        """更新文件计数标签"""
        current_index = self.file_manager.get_current_index()
        total_count = self.file_manager.get_file_count()
        self.file_count_label.config(text=f"{current_index + 1}/{total_count}")
    
    def on_process_type_change(self):
        """处理方式变化时的处理"""
        process_type = self.process_type_var.get()
        if process_type == "resize":
            self.create_resize_params()
        else:
            # 清空参数区域
            for widget in self.params_frame.winfo_children():
                widget.destroy()
    
    def on_resize_mode_change(self):
        """调整方式变化时的处理"""
        resize_mode = self.resize_mode_var.get()
        if resize_mode == "percentage":
            self.create_percentage_input()
        else:
            self.create_dimensions_input()
    
    def on_output_mode_change(self, *args):
        """输出方式变化时的处理"""
        output_mode = self.output_mode_var.get()
        if output_mode == "custom_dir":
            self.select_output_btn.config(state=tk.NORMAL)
        else:
            self.select_output_btn.config(state=tk.DISABLED)
    
    def select_output_directory(self):
        """选择输出目录"""
        directory_path = filedialog.askdirectory(title="选择输出目录")
        if directory_path:
            self.output_directory = directory_path
            self.status_label.config(text=f"输出目录: {directory_path}")
    
    def get_process_params(self):
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
            
            return {
                'resize_mode': resize_mode,
                'resize_value': resize_value,
                'quality': 85
            }
        else:
            return {}
    
    def process_image(self):
        """处理当前图片"""
        if not self.current_image_path:
            return
        
        if self.is_processing:
            messagebox.showwarning("正在处理", "请等待当前处理完成")
            return
        
        # 获取处理参数
        process_params = self.get_process_params()
        
        # 在新线程中处理图片
        self.processing_thread = threading.Thread(
            target=self._process_image_thread,
            args=(self.current_image_path, process_params)
        )
        self.processing_thread.start()
    
    def _process_image_thread(self, image_path, process_params):
        """处理图片的线程函数"""
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        try:
            process_type = self.process_type_var.get()
            output_mode = self.output_mode_var.get()
            
            # 获取输出路径
            if output_mode == "custom_dir" and hasattr(self, 'output_directory'):
                output_path = self.file_manager.get_output_path(
                    image_path, output_mode, self.output_directory
                )
            else:
                output_path = self.file_manager.get_output_path(image_path, output_mode)
            
            # 创建备份（如果是覆盖模式）
            if output_mode == "overwrite":
                self.file_manager.create_backup(image_path)
            
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="正在处理..."))
            
            # 处理图片
            result = self.processor.process_single_image(
                image_path, output_path, process_type, process_params
            )
            
            # 在主线程中更新UI
            self.root.after(0, lambda: self.on_process_complete(result, output_path))
            
        except Exception as e:
            self.root.after(0, lambda: self.on_process_error(str(e)))
        
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
    
    def on_process_complete(self, result, output_path):
        """处理完成时的回调"""
        if result['success']:
            # 显示处理后的图片
            self.display_image(output_path, self.processed_label)
            
            # 显示结果信息
            input_size = result['input_size']
            output_size = result['output_size']
            compression_ratio = result.get('compression_ratio', 0)
            
            info_text = f"处理完成! 输入: {input_size//1024}KB, 输出: {output_size//1024}KB"
            if compression_ratio > 0:
                info_text += f", 压缩率: {compression_ratio:.1f}%"
            
            self.status_label.config(text=info_text)
            messagebox.showinfo("处理完成", info_text)
        else:
            self.status_label.config(text="处理失败")
            messagebox.showerror("处理失败", result.get('error', '未知错误'))
    
    def on_process_error(self, error_message):
        """处理错误时的回调"""
        self.status_label.config(text="处理失败")
        messagebox.showerror("处理错误", error_message)
    
    def stop_processing(self):
        """停止处理"""
        self.processor.stop_all_processing()
        self.status_label.config(text="正在停止...")
    
    def batch_process_images(self):
        """批量处理图片"""
        files = self.file_manager.current_files
        if not files:
            messagebox.showwarning("无文件", "请先选择包含图片的文件夹")
            return
        
        if self.is_processing:
            messagebox.showwarning("正在处理", "请等待当前处理完成")
            return
        
        # 确认批量处理
        result = messagebox.askyesno(
            "确认批量处理", 
            f"确定要处理 {len(files)} 个图片文件吗？"
        )
        
        if result:
            # 获取处理参数
            process_params = self.get_process_params()
            
            # 设置进度回调
            self.processor.set_processing_callback(self.on_batch_progress)
            
            # 在新线程中批量处理
            self.processing_thread = threading.Thread(
                target=self._batch_process_thread,
                args=(files, process_params)
            )
            self.processing_thread.start()
    
    def _batch_process_thread(self, files, process_params):
        """批量处理的线程函数"""
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.batch_process_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        try:
            process_type = self.process_type_var.get()
            output_mode = self.output_mode_var.get()
            
            output_dir = None
            if output_mode == "custom_dir" and hasattr(self, 'output_directory'):
                output_dir = self.output_directory
            
            # 批量处理
            results = self.processor.process_multiple_images(
                files, output_mode, process_type, process_params, output_dir
            )
            
            # 在主线程中显示结果
            self.root.after(0, lambda: self.on_batch_process_complete(results))
            
        except Exception as e:
            self.root.after(0, lambda: self.on_batch_process_error(str(e)))
        
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.batch_process_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.progress_var.set(0))
    
    def on_batch_progress(self, file_path, current, total):
        """批量处理进度回调"""
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.status_label.config(text=f"正在处理: {os.path.basename(file_path)} ({current}/{total})")
    
    def on_batch_process_complete(self, results):
        """批量处理完成时的回调"""
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        summary = f"批量处理完成! 成功: {success_count}/{total_count}"
        if success_count < total_count:
            summary += f", 失败: {total_count - success_count}"
        
        self.status_label.config(text=summary)
        messagebox.showinfo("批量处理完成", summary)
    
    def on_batch_process_error(self, error_message):
        """批量处理错误时的回调"""
        self.status_label.config(text="批量处理失败")
        messagebox.showerror("批量处理错误", error_message)