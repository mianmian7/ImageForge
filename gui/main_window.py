"""
主窗口GUI模块（重构版）
负责应用程序整体布局和管理器协调
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import threading
from typing import Optional, List, Dict, Any

from core.image_processor import ImageProcessor
from core.file_manager import FileManager
from gui.asset_cleaner_panel import AssetCleanerPanel
from gui.managers.status_bar_manager import StatusBarManager
from gui.managers.preview_manager import PreviewManager
from gui.managers.file_manager_view import FileManagerView
from gui.managers.process_control_manager import ProcessControlManager
from utils.logger import get_logger

logger = get_logger(__name__)


class ImageProcessorGUI:
    """图像处理器主窗口类（协调器）"""
    
    def __init__(self, root, config):
        """
        初始化主窗口
        
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
        
        # 处理相关
        self.processing_thread = None
        self.is_processing = False
        
        # 处理结果缓存
        self.processed_results = {}  # 存储输入路径到输出路径的映射
        
        # 设置窗口标题
        self.root.title("ImageForge - 图像处理器")
        
        # 初始化管理器
        self._init_managers()
        
        # 设置管理器回调
        self._setup_callbacks()
        
        # 设置UI布局
        self.setup_ui()
        
        # 加载配置
        self.file_manager_view.load_configurations()
    
    def _init_managers(self):
        """初始化所有管理器"""
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # 初始化状态栏管理器
        self.status_bar = StatusBarManager(self.main_frame)
        
        # 预览管理器和处理控制管理器将在 create_main_content_area() 中创建
        self.preview_manager = None
        self.process_control = None
        
        # 创建文件管理视图（需要在资源清理面板创建后设置）
        self.file_manager_view = None  # 稍后初始化
    
    def _setup_callbacks(self):
        """设置管理器间的回调函数"""
        # 文件管理视图回调将在创建后设置
        pass
    
    def setup_ui(self):
        """设置用户界面布局"""
        # 配置根窗口网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 主框架布局
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置主框架网格权重
        self.main_frame.columnconfigure(0, weight=2)  # 左侧内容区域
        self.main_frame.columnconfigure(1, weight=1)  # 右侧面板区域
        self.main_frame.rowconfigure(0, weight=0)     # 文件选择区域
        self.main_frame.rowconfigure(1, weight=1)     # 预览和控制区域
        self.main_frame.rowconfigure(2, weight=0)     # 状态栏区域
        
        # 创建资源清理面板（右侧）
        self.create_asset_cleaner_panel()
        
        # 现在可以创建文件管理视图了（因为需要asset_cleaner_panel）
        self.file_manager_view = FileManagerView(
            self.main_frame, self.config, self.file_manager, self.asset_cleaner_panel
        )
        self.file_manager_view.set_callbacks(
            on_file_selected=self.on_file_selected,
            on_navigation=self.on_navigation,
            on_filter_changed=self.on_filter_changed
        )
        
        # 放置文件选择区域（跨越两列）
        self.file_manager_view.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 创建左右分区
        self.create_main_content_area()
        
        # 放置状态栏（跨越两列）
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_main_content_area(self):
        """创建主内容区域（左右分区）"""
        # 左侧内容区域
        left_frame = ttk.Frame(self.main_frame)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        left_frame.rowconfigure(0, weight=1)     # 预览区域
        left_frame.rowconfigure(1, weight=0)     # 控制面板
        left_frame.columnconfigure(0, weight=1)
        
        # 创建预览管理器（使用 left_frame 作为父容器）
        self.preview_manager = PreviewManager(left_frame, self.config, self.processor)
        self.preview_manager.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 创建处理控制管理器（使用 left_frame 作为父容器）
        self.process_control = ProcessControlManager(
            left_frame, self.config, self.processor, self.file_manager
        )
        self.process_control.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
    
    def create_asset_cleaner_panel(self):
        """创建资源清理面板"""
        right_frame = ttk.Frame(self.main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        
        self.asset_cleaner_panel = AssetCleanerPanel(
            right_frame, 
            self.config, 
            self.select_folder_dialog,
            self.set_directory_from_asset_cleaner
        )
        
        self.asset_cleaner_panel.panel_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def select_folder_dialog(self, title="选择文件夹"):
        """统一的文件夹选择对话框"""
        from tkinter import filedialog
        return filedialog.askdirectory(title=title)
    
    def set_directory_from_asset_cleaner(self, directory_path):
        """从资源清理面板同步文件夹路径到主窗口"""
        if directory_path:
            self.file_manager_view.set_file_path(directory_path)
            self.processed_results.clear()
            
            filters = self.file_manager_view.get_current_filters()
            files = self.file_manager.select_directory_with_filter_and_sort(
                directory_path, filters['recursive'], 
                filters['resolution'], filters['sort'], filters['format']
            )
            
            if files:
                self.load_image(files[0])
                self.file_manager_view.update_navigation_buttons()
                self.file_manager_view.update_file_count_label()
                self.process_control.enable_batch_processing(True)
                
                parts = [f"已同步并加载 {len(files)} 个图片文件"]
                if filters['recursive']:
                    parts.append("及其子目录")
                if filters['resolution']['enabled']:
                    parts.append(f"(分辨率≥{filters['resolution']['min_width']}×{filters['resolution']['min_height']})")
                
                self.status_bar.set_status("".join(parts))
            else:
                self.current_image_path = ""
                self.preview_manager.clear_all()
                self.process_control.enable_processing(False)
                self.process_control.enable_batch_processing(False)
                self.file_manager_view.update_navigation_buttons()
                self.file_manager_view.update_file_count_label()
                
                self.status_bar.set_status(f"已同步到文件夹: {directory_path} (无支持的图片文件)")
    
    def on_file_selected(self, file_path: str, is_single: bool = True, all_files: List[str] = None):
        """文件选择回调"""
        self.processed_results.clear()
        self.load_image(file_path)
        
        if not is_single and all_files:
            self.file_manager_view.update_navigation_buttons()
            self.file_manager_view.update_file_count_label()
            self.process_control.enable_batch_processing(True)
            
            filters = self.file_manager_view.get_current_filters()
            parts = [f"已加载 {len(all_files)} 个图片文件"]
            if filters['recursive']:
                parts.append("及其子目录")
            if filters['resolution']['enabled']:
                parts.append(f"(分辨率≥{filters['resolution']['min_width']}×{filters['resolution']['min_height']})")
            if filters['format']:
                format_name = "、".join([ext.replace('.', '') for ext in filters['format']])
                parts.append(f"(仅{format_name}格式)")
            
            self.status_bar.set_status("".join(parts))
    
    def on_navigation(self, file_path: str):
        """导航回调"""
        self.load_image(file_path)
    
    def on_filter_changed(self):
        """过滤选项变化回调"""
        if not self.file_manager.current_directory:
            return
        
        filters = self.file_manager_view.get_current_filters()
        files = self.file_manager.select_directory_with_filter_and_sort(
            self.file_manager.current_directory, filters['recursive'],
            filters['resolution'], filters['sort'], filters['format']
        )
        
        if files:
            # 保留仍在列表中的处理结果
            current_files_set = set(files)
            self.processed_results = {
                k: v for k, v in self.processed_results.items() if k in current_files_set
            }
            
            self.load_image(files[0])
            self.file_manager_view.update_navigation_buttons()
            self.file_manager_view.update_file_count_label()
            
            parts = [f"已重新加载 {len(files)} 个图片文件"]
            if filters['recursive']:
                parts.append("及其子目录")
            if filters['resolution']['enabled']:
                parts.append(f"(分辨率≥{filters['resolution']['min_width']}×{filters['resolution']['min_height']})")
            
            self.status_bar.set_status("".join(parts))
        else:
            self.processed_results.clear()
            self.current_image_path = ""
            self.preview_manager.clear_all()
            self.process_control.enable_processing(False)
            self.process_control.enable_batch_processing(False)
            self.status_bar.set_status("所选文件夹中没有找到支持的图片文件")
    
    def load_image(self, image_path: str):
        """加载图片"""
        try:
            self.current_image_path = image_path
            self.file_manager_view.set_file_path(image_path)
            
            # 显示原图
            self.preview_manager.display_original(image_path)
            
            # 检查是否有处理结果
            if image_path in self.processed_results:
                processed_path = self.processed_results[image_path]
                if os.path.exists(processed_path):
                    self.preview_manager.display_processed(processed_path)
                else:
                    self.preview_manager.clear_processed()
                    del self.processed_results[image_path]
            else:
                self.preview_manager.clear_processed()
            
            # 启用处理按钮
            self.process_control.enable_processing(True)
            
            # 更新状态
            self.status_bar.set_status(f"已加载: {os.path.basename(image_path)}")
            
        except Exception as e:
            logger.error(f"加载图片失败: {image_path}, 错误: {e}")
            messagebox.showerror("加载失败", f"无法加载图片: {str(e)}")
    
    def process_image(self):
        """处理当前图片"""
        if not self.current_image_path:
            return
        
        if self.is_processing:
            messagebox.showwarning("正在处理", "请等待当前处理完成")
            return
        
        process_params = self.process_control.get_process_params()
        if process_params is None:
            return
        
        self.processing_thread = threading.Thread(
            target=self._process_image_thread,
            args=(self.current_image_path, process_params)
        )
        self.processing_thread.start()
    
    def _process_image_thread(self, image_path, process_params):
        """处理图片的线程函数"""
        self.is_processing = True
        self.process_control.set_processing_state(True)
        
        try:
            process_type = self.process_control.get_process_type()
            output_mode = self.process_control.get_output_mode()
            
            output_format = process_params.get('output_format')
            
            output_dir = self.process_control.get_output_directory() if output_mode == "custom_dir" else None
            output_path = self.file_manager.get_output_path(image_path, output_mode, output_dir, output_format)
            
            if output_mode == "overwrite":
                self.file_manager.create_backup(image_path)
            
            self.root.after(0, lambda: self.status_bar.set_status("正在处理..."))
            
            result = self.processor.process_single_image(
                image_path, output_path, process_type, process_params
            )
            
            self.root.after(0, lambda: self.on_process_complete(result, output_path))
            
        except Exception as e:
            logger.exception(f"处理图片时发生错误: {image_path}")
            self.root.after(0, lambda: self.on_process_error(str(e)))
        
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.process_control.set_processing_state(False))
    
    def on_process_complete(self, result, output_path):
        """处理完成回调"""
        if result['success']:
            self.processed_results[self.current_image_path] = output_path
            self.preview_manager.display_processed(output_path)
            
            input_size = result['input_size']
            output_size = result['output_size']
            compression_ratio = result.get('compression_ratio', 0)
            
            info_text = f"处理完成! 输入: {input_size//1024}KB, 输出: {output_size//1024}KB"
            if compression_ratio > 0:
                info_text += f", 压缩率: {compression_ratio:.1f}%"
            
            self.status_bar.set_status(info_text)
            messagebox.showinfo("处理完成", info_text)
        else:
            self.status_bar.set_status("处理失败")
            messagebox.showerror("处理失败", result.get('error', '未知错误'))
    
    def on_process_error(self, error_message):
        """处理错误回调"""
        self.status_bar.set_status("处理失败")
        messagebox.showerror("处理错误", error_message)
    
    def batch_process_images(self):
        """批量处理图片"""
        files = self.file_manager.current_files
        if not files:
            messagebox.showwarning("无文件", "请先选择包含图片的文件夹")
            return
        
        if self.is_processing:
            messagebox.showwarning("正在处理", "请等待当前处理完成")
            return
        
        process_params = self.process_control.get_process_params()
        if process_params is None:
            return
        
        result = messagebox.askyesno("确认批量处理", f"确定要处理 {len(files)} 个图片文件吗？")
        if result:
            self.processor.set_processing_callback(self.on_batch_progress)
            self.processing_thread = threading.Thread(
                target=self._batch_process_thread,
                args=(files, process_params)
            )
            self.processing_thread.start()
    
    def _batch_process_thread(self, files, process_params):
        """批量处理线程函数"""
        self.is_processing = True
        self.process_control.set_processing_state(True)
        
        try:
            process_type = self.process_control.get_process_type()
            output_mode = self.process_control.get_output_mode()
            output_dir = self.process_control.get_output_directory() if output_mode == "custom_dir" else None
            
            results = self.processor.process_multiple_images(
                files, output_mode, process_type, process_params, output_dir
            )
            
            self.root.after(0, lambda: self.on_batch_process_complete(results))
            
        except Exception as e:
            logger.exception("批量处理时发生错误")
            self.root.after(0, lambda: self.on_batch_process_error(str(e)))
        
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.process_control.set_processing_state(False))
            self.root.after(0, lambda: self.status_bar.reset_progress())
    
    def on_batch_progress(self, file_path, current, total):
        """批量处理进度回调"""
        progress = (current / total) * 100
        self.status_bar.set_progress(progress)
        self.status_bar.set_status(f"正在处理: {os.path.basename(file_path)} ({current}/{total})")
    
    def on_batch_process_complete(self, results):
        """批量处理完成回调"""
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        # 保存处理结果
        for result in results:
            if result['success'] and result.get('output_path') and result.get('input_path'):
                self.processed_results[result['input_path']] = result['output_path']
        
        # 计算统计信息
        total_input_size = 0
        total_output_size = 0
        successful_results = [r for r in results if r['success'] and r.get('input_size', 0) > 0]
        
        for result in successful_results:
            total_input_size += result.get('input_size', 0)
            total_output_size += result.get('output_size', 0)
        
        from utils.common_utils import format_file_size
        
        message_lines = [f"批量处理完成！", f"成功: {success_count}/{total_count}"]
        if success_count < total_count:
            message_lines.append(f"失败: {total_count - success_count}")
        message_lines.append("")
        
        status_summary_parts = [f"批量处理完成! 成功: {success_count}/{total_count}"]
        
        if successful_results and total_input_size > 0:
            saved_size = total_input_size - total_output_size
            saved_percentage = (saved_size / total_input_size) * 100
            
            message_lines.append("压缩统计：")
            message_lines.append(f"原始总大小: {format_file_size(total_input_size)}")
            message_lines.append(f"压缩后总大小: {format_file_size(total_output_size)}")
            message_lines.append(f"节省空间: {format_file_size(saved_size)}")
            message_lines.append(f"压缩比例: {saved_percentage:.1f}%")
            
            status_summary_parts.append(f"总大小: {format_file_size(total_input_size)} -> {format_file_size(total_output_size)}")
            status_summary_parts.append(f"节省: {format_file_size(saved_size)} ({saved_percentage:.1f}%)")
        
        summary = "\n".join(message_lines)
        status_summary_text = " | ".join(status_summary_parts)
        self.status_bar.set_status(status_summary_text)
        
        # 显示第一个成功的处理结果
        for result in results:
            if result['success'] and result.get('output_path'):
                if self.current_image_path and result['input_path'] == self.current_image_path:
                    self.preview_manager.display_processed(result['output_path'])
                    break
        
        messagebox.showinfo("批量处理完成", summary)
    
    def on_batch_process_error(self, error_message):
        """批量处理错误回调"""
        self.status_bar.set_status("批量处理失败")
        messagebox.showerror("批量处理错误", error_message)
    
    # 连接处理控制管理器的处理方法
    def connect_process_control(self):
        """连接处理控制管理器的方法"""
        # 替换process_control中的占位方法
        self.process_control.process_image = self.process_image
        self.process_control.batch_process_images = self.batch_process_images


# 在__init__末尾调用连接方法
def _finalize_init(self):
    """完成初始化"""
    self.connect_process_control()

# 将finalize方法添加到__init__中
ImageProcessorGUI._original_init = ImageProcessorGUI.__init__

def _new_init(self, root, config):
    self._original_init(root, config)
    self.connect_process_control()

ImageProcessorGUI.__init__ = _new_init