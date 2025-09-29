"""
文件管理视图模块
管理文件选择、导航、过滤和排序
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable, Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


class FileManagerView:
    """文件管理视图管理器类"""
    
    def __init__(self, parent: tk.Widget, config, file_manager, asset_cleaner_panel=None):
        """初始化文件管理视图管理器"""
        self.parent = parent
        self.config = config
        self.file_manager = file_manager
        self.asset_cleaner_panel = asset_cleaner_panel
        
        # 回调函数
        self.on_file_selected_callback = None
        self.on_navigation_callback = None
        self.on_filter_changed_callback = None
        
        # UI 组件
        self.file_frame = None
        self.file_path_var = None
        self.prev_btn = None
        self.next_btn = None
        self.file_count_label = None
        
        # 过滤和排序选项
        self.recursive_var = None
        self.resolution_filter_var = None
        self.min_width_var = None
        self.min_height_var = None
        self.format_filter_var = None
        self.sort_option_var = None
        
        # UI子组件
        self.resolution_input_frame = None
        self.recursive_hint_label = None
        self.resolution_hint_label = None
        self.format_hint_label = None
        self.sort_hint_label = None
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """创建文件管理组件"""
        self.file_frame = ttk.LabelFrame(self.parent, text="文件选择", padding="5")
        
        # 文件路径显示和按钮
        self.file_path_var = tk.StringVar()
        file_path_entry = ttk.Entry(self.file_frame, textvariable=self.file_path_var, width=60)
        file_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        select_file_btn = ttk.Button(self.file_frame, text="选择文件", command=self._select_single_file)
        select_file_btn.grid(row=0, column=1, padx=(0, 5))
        
        select_folder_btn = ttk.Button(self.file_frame, text="选择文件夹", command=self._select_directory)
        select_folder_btn.grid(row=0, column=2, padx=(0, 5))
        
        self.prev_btn = ttk.Button(self.file_frame, text="上一张", command=self._show_previous_image, state=tk.DISABLED)
        self.prev_btn.grid(row=0, column=3, padx=(0, 5))
        
        self.next_btn = ttk.Button(self.file_frame, text="下一张", command=self._show_next_image, state=tk.DISABLED)
        self.next_btn.grid(row=0, column=4)
        
        self.file_count_label = ttk.Label(self.file_frame, text="0/0")
        self.file_count_label.grid(row=0, column=5, padx=(10, 0))
        
        self._create_recursive_options()
        self._create_resolution_filter_options()
        self._create_format_filter_options()
        self._create_sort_options()
        
        self.file_frame.columnconfigure(0, weight=1)
    
    def _create_recursive_options(self):
        """创建递归选项"""
        recursive_frame = ttk.Frame(self.file_frame)
        recursive_frame.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(2, 2))
        
        self.recursive_var = tk.BooleanVar(value=True)
        recursive_check = ttk.Checkbutton(recursive_frame, text="递归读取子目录", 
                                        variable=self.recursive_var, command=self._on_recursive_change)
        recursive_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.recursive_hint_label = ttk.Label(recursive_frame, text="(勾选后读取文件夹及其所有子文件夹中的图片)", 
                                           foreground="gray", font=("Arial", 9))
        self.recursive_hint_label.pack(side=tk.LEFT)
    
    def _create_resolution_filter_options(self):
        """创建分辨率过滤选项"""
        filter_frame = ttk.Frame(self.file_frame)
        filter_frame.grid(row=2, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(2, 2))
        
        self.resolution_filter_var = tk.BooleanVar(value=False)
        filter_check = ttk.Checkbutton(filter_frame, text="启用分辨率过滤", 
                                     variable=self.resolution_filter_var, command=self._on_resolution_filter_change)
        filter_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.resolution_input_frame = ttk.Frame(filter_frame)
        self.resolution_input_frame.pack(side=tk.LEFT)
        
        ttk.Label(self.resolution_input_frame, text="最小分辨率:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.min_width_var = tk.StringVar(value="1920")
        width_spinbox = ttk.Spinbox(self.resolution_input_frame, from_=1, to=10000, 
                                   textvariable=self.min_width_var, width=8)
        width_spinbox.pack(side=tk.LEFT, padx=(0, 2))
        
        ttk.Label(self.resolution_input_frame, text="×").pack(side=tk.LEFT, padx=(2, 2))
        
        self.min_height_var = tk.StringVar(value="1080")
        height_spinbox = ttk.Spinbox(self.resolution_input_frame, from_=1, to=10000, 
                                    textvariable=self.min_height_var, width=8)
        height_spinbox.pack(side=tk.LEFT, padx=(2, 5))
        
        ttk.Label(self.resolution_input_frame, text="像素").pack(side=tk.LEFT)
        
        self.resolution_hint_label = ttk.Label(filter_frame, text="(启用后只处理等于或高于指定分辨率的图片)", 
                                             foreground="gray", font=("Arial", 9))
        self.resolution_hint_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self.min_width_var.trace('w', self._on_resolution_filter_value_change)
        self.min_height_var.trace('w', self._on_resolution_filter_value_change)
    
    def _create_format_filter_options(self):
        """创建格式过滤选项"""
        format_frame = ttk.Frame(self.file_frame)
        format_frame.grid(row=3, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(2, 2))

        ttk.Label(format_frame, text="图片格式:").pack(side=tk.LEFT, padx=(0, 10))

        self.format_filter_var = tk.StringVar(value="全部格式")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_filter_var,
                                   values=["全部格式", "仅JPEG", "仅PNG", "仅BMP", "仅GIF", "仅TIFF", "仅WEBP"],
                                   width=12, state="readonly")
        format_combo.pack(side=tk.LEFT, padx=(0, 10))

        self.format_hint_label = ttk.Label(format_frame, text="(选择要读取的图片格式类型)",
                                         foreground="gray", font=("Arial", 9))
        self.format_hint_label.pack(side=tk.LEFT, padx=(10, 0))

        self.format_filter_var.trace('w', self._on_format_filter_change)
    
    def _create_sort_options(self):
        """创建排序选项"""
        sort_frame = ttk.Frame(self.file_frame)
        sort_frame.grid(row=4, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(2, 2))

        ttk.Label(sort_frame, text="文件排序:").pack(side=tk.LEFT, padx=(0, 10))

        self.sort_option_var = tk.StringVar(value="file_size_desc")
        sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_option_var,
                                 values=["按文件大小(大到小)", "按文件大小(小到大)",
                                        "按分辨率宽度(大到小)", "按分辨率宽度(小到大)",
                                        "按分辨率高度(大到小)", "按分辨率高度(小到大)",
                                        "按文件名(A-Z)", "按文件名(Z-A)"],
                                 width=18, state="readonly")
        sort_combo.pack(side=tk.LEFT, padx=(0, 10))

        self.sort_hint_label = ttk.Label(sort_frame, text="(选择文件列表排序方式)",
                                       foreground="gray", font=("Arial", 9))
        self.sort_hint_label.pack(side=tk.LEFT, padx=(10, 0))

        self.sort_option_var.trace('w', self._on_sort_option_change)
    
    def _setup_layout(self):
        """设置组件布局"""
        self._on_resolution_filter_change()
    
    def _select_single_file(self):
        """选择单个文件"""
        format_filter = self._get_format_filter_config()
        if format_filter:
            format_patterns = [f"*{ext}" for ext in format_filter]
            filter_name = self.format_filter_var.get().replace("仅", "")
            filetypes = [(f"{filter_name}文件", " ".join(format_patterns)), ("所有文件", "*.*")]
        else:
            filetypes = [("所有文件", "*.*"), ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp")]

        file_path = filedialog.askopenfilename(title="选择图片文件", filetypes=filetypes)
        if file_path and self.on_file_selected_callback:
            self.on_file_selected_callback(file_path, is_single=True)
    
    def _select_directory(self):
        """选择文件夹"""
        directory_path = filedialog.askdirectory(title="选择包含图片的文件夹")
        if directory_path:
            if self.asset_cleaner_panel:
                self.asset_cleaner_panel.set_project_directory(directory_path)

            files = self.file_manager.select_directory_with_filter_and_sort(
                directory_path, self.recursive_var.get(), 
                self._get_resolution_filter_config(), 
                self._get_sort_config(), 
                self._get_format_filter_config()
            )
            
            if files and self.on_file_selected_callback:
                self.on_file_selected_callback(files[0], is_single=False, all_files=files)
                self.update_navigation_buttons()
                self.update_file_count_label()
            elif not files:
                resolution_filter = self._get_resolution_filter_config()
                format_filter = self._get_format_filter_config()
                error_parts = ["所选文件夹中没有找到支持的图片文件"]
                if resolution_filter['enabled']:
                    error_parts.append(f"(分辨率要求≥{resolution_filter['min_width']}×{resolution_filter['min_height']})")
                if format_filter:
                    format_name = self.format_filter_var.get().replace("仅", "")
                    error_parts.append(f"(格式要求: {format_name})")
                messagebox.showwarning("无图片文件", " ".join(error_parts))
    
    def _show_previous_image(self):
        """显示上一张图片"""
        prev_file = self.file_manager.get_previous_file()
        if prev_file and self.on_navigation_callback:
            self.on_navigation_callback(prev_file)
            self.update_file_count_label()
    
    def _show_next_image(self):
        """显示下一张图片"""
        next_file = self.file_manager.get_next_file()
        if next_file and self.on_navigation_callback:
            self.on_navigation_callback(next_file)
            self.update_file_count_label()
    
    def _on_recursive_change(self):
        """处理递归选项变更"""
        if self.recursive_var.get():
            self.recursive_hint_label.config(text="(勾选后读取文件夹及其所有子文件夹中的图片)")
        else:
            self.recursive_hint_label.config(text="(取消勾选后只读取当前文件夹中的图片)")
        if self.file_manager.current_directory and self.on_filter_changed_callback:
            self.on_filter_changed_callback()
    
    def _on_resolution_filter_change(self):
        """处理分辨率过滤选项变更"""
        if self.resolution_filter_var.get():
            self.resolution_input_frame.pack(side=tk.LEFT)
            self.resolution_hint_label.config(text="(启用后只处理等于或高于指定分辨率的图片)")
        else:
            self.resolution_input_frame.pack_forget()
            self.resolution_hint_label.config(text="(禁用后将处理所有图片文件)")
        self._save_resolution_filter_config()
        if self.file_manager.current_directory and self.on_filter_changed_callback:
            self.on_filter_changed_callback()
    
    def _on_resolution_filter_value_change(self, *args):
        """处理分辨率过滤数值变化"""
        self._save_resolution_filter_config()
        if self.file_manager.current_directory and self.on_filter_changed_callback:
            self.on_filter_changed_callback()
    
    def _on_format_filter_change(self, *args):
        """处理图片格式筛选变化"""
        self._save_format_filter_config()
        if self.file_manager.current_directory and self.on_filter_changed_callback:
            self.on_filter_changed_callback()
    
    def _on_sort_option_change(self, *args):
        """处理排序选项变化"""
        self._save_sort_config()
        if self.file_manager.current_directory and self.on_filter_changed_callback:
            self.on_filter_changed_callback()
    
    def _get_resolution_filter_config(self) -> Dict[str, Any]:
        """获取分辨率过滤配置"""
        return {
            'enabled': self.resolution_filter_var.get(),
            'min_width': int(self.min_width_var.get()),
            'min_height': int(self.min_height_var.get())
        }
    
    def _get_format_filter_config(self) -> Optional[List[str]]:
        """获取图片格式筛选配置"""
        format_map = {
            "全部格式": None, "仅JPEG": ['.jpg', '.jpeg'], "仅PNG": ['.png'],
            "仅BMP": ['.bmp'], "仅GIF": ['.gif'], "仅TIFF": ['.tiff'], "仅WEBP": ['.webp']
        }
        return format_map.get(self.format_filter_var.get(), None)
    
    def _get_sort_config(self) -> str:
        """获取排序配置"""
        sort_option_map = {
            "按文件大小(大到小)": "file_size_desc", "按文件大小(小到大)": "file_size_asc",
            "按分辨率宽度(大到小)": "width_desc", "按分辨率宽度(小到大)": "width_asc",
            "按分辨率高度(大到小)": "height_desc", "按分辨率高度(小到大)": "height_asc",
            "按文件名(A-Z)": "filename_asc", "按文件名(Z-A)": "filename_desc"
        }
        return sort_option_map.get(self.sort_option_var.get(), "file_size_desc")
    
    def _save_resolution_filter_config(self):
        """保存分辨率过滤配置"""
        try:
            filter_config = self._get_resolution_filter_config()
            self.config.set_resolution_filter_config(
                filter_config['enabled'], filter_config['min_width'], filter_config['min_height'])
            self.config.save_config()
        except Exception as e:
            logger.error(f"保存分辨率过滤配置失败: {e}")
    
    def _save_format_filter_config(self):
        """保存格式筛选配置"""
        try:
            self.config.set('format_filter', self.format_filter_var.get())
            self.config.save_config()
        except Exception as e:
            logger.error(f"保存格式筛选配置失败: {e}")
    
    def _save_sort_config(self):
        """保存排序配置"""
        try:
            self.config.set_sort_config(self._get_sort_config())
            self.config.save_config()
        except Exception as e:
            logger.error(f"保存排序配置失败: {e}")
    
    def load_configurations(self):
        """加载所有配置"""
        try:
            filter_config = self.config.get_resolution_filter_config()
            self.resolution_filter_var.set(filter_config['enabled'])
            self.min_width_var.set(str(filter_config['min_width']))
            self.min_height_var.set(str(filter_config['min_height']))
            
            format_config = self.config.get('format_filter', '全部格式')
            self.format_filter_var.set(format_config)
            
            sort_config = self.config.get_sort_config()
            sort_option_map = {
                "file_size_desc": "按文件大小(大到小)", "file_size_asc": "按文件大小(小到大)", 
                "width_desc": "按分辨率宽度(大到小)", "width_asc": "按分辨率宽度(小到大)",
                "height_desc": "按分辨率高度(大到小)", "height_asc": "按分辨率高度(小到大)",
                "filename_asc": "按文件名(A-Z)", "filename_desc": "按文件名(Z-A)"
            }
            self.sort_option_var.set(sort_option_map.get(sort_config, "按文件大小(大到小)"))
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
    
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
    
    def set_file_path(self, path: str):
        """设置文件路径显示"""
        self.file_path_var.set(path)
    
    def get_file_path(self) -> str:
        """获取当前文件路径"""
        return self.file_path_var.get()
    
    def set_callbacks(self, on_file_selected: Callable = None, 
                     on_navigation: Callable = None, on_filter_changed: Callable = None):
        """设置回调函数"""
        self.on_file_selected_callback = on_file_selected
        self.on_navigation_callback = on_navigation
        self.on_filter_changed_callback = on_filter_changed
    
    def get_current_filters(self) -> Dict[str, Any]:
        """获取当前所有过滤配置"""
        return {
            'recursive': self.recursive_var.get(),
            'resolution': self._get_resolution_filter_config(),
            'format': self._get_format_filter_config(),
            'sort': self._get_sort_config()
        }
    
    def grid(self, **kwargs):
        """放置文件管理区域到指定位置"""
        self.file_frame.grid(**kwargs)
