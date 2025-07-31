"""
Asset Cleaner GUI Panel
提供资源清理功能的用户界面组件
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from typing import Optional

from utils.asset_cleaner import clean_start, size_start


class AssetCleanerPanel:
    """资源清理面板类"""
    
    def __init__(self, parent, config):
        """初始化资源清理面板
        
        Args:
            parent: 父容器
            config: 配置管理器
        """
        self.parent = parent
        self.config = config
        
        # 当前处理状态
        self.is_processing = False
        self.processing_thread = None
        
        # 创建面板
        self.create_panel()
    
    def create_panel(self):
        """创建资源清理面板"""
        # 创建主框架
        panel_frame = ttk.LabelFrame(self.parent, text="资源清理工具", padding="8")
        panel_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(10, 0))
        
        # 配置网格权重
        panel_frame.columnconfigure(0, weight=1)
        panel_frame.rowconfigure(4, weight=1)
        
        # 创建各个控件
        self.create_directory_controls(panel_frame)
        self.create_analysis_controls(panel_frame)
        self.create_action_controls(panel_frame)
        self.create_results_display(panel_frame)
    
    def create_directory_controls(self, parent):
        """创建目录选择控件"""
        # 目录选择框架
        dir_frame = ttk.Frame(parent)
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="项目目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.project_dir_var = tk.StringVar()
        self.project_dir_entry = ttk.Entry(dir_frame, textvariable=self.project_dir_var, width=30)
        self.project_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_dir_btn = ttk.Button(dir_frame, text="浏览", command=self.browse_project_directory)
        self.browse_dir_btn.grid(row=0, column=2)
    
    def create_analysis_controls(self, parent):
        """创建分析类型控件"""
        # 分析类型框架
        analysis_frame = ttk.Frame(parent)
        analysis_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        ttk.Label(analysis_frame, text="分析类型:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.analysis_type_var = tk.StringVar(value="size")
        
        size_radio = ttk.Radiobutton(
            analysis_frame, 
            text="分析资源大小", 
            variable=self.analysis_type_var, 
            value="size",
            command=self.on_analysis_type_change
        )
        size_radio.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        clean_radio = ttk.Radiobutton(
            analysis_frame, 
            text="清理未使用资源", 
            variable=self.analysis_type_var, 
            value="clean",
            command=self.on_analysis_type_change
        )
        clean_radio.grid(row=0, column=2, sticky=tk.W)
    
    def create_action_controls(self, parent):
        """创建操作控件"""
        # 操作框架
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # 输出文件选择
        ttk.Label(action_frame, text="输出文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.output_file_var = tk.StringVar()
        self.output_file_entry = ttk.Entry(action_frame, textvariable=self.output_file_var, width=25)
        self.output_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_output_btn = ttk.Button(action_frame, text="选择", command=self.browse_output_file)
        self.browse_output_btn.grid(row=0, column=2, padx=(0, 10))
        
        # 分析按钮
        self.run_analysis_btn = ttk.Button(action_frame, text="开始分析", command=self.run_analysis)
        self.run_analysis_btn.grid(row=0, column=3)
        
        action_frame.columnconfigure(1, weight=1)
        
        # 删除选项（仅在清理模式下显示）
        self.delete_option_frame = ttk.Frame(parent)
        self.delete_option_frame.grid(row=3, column=0, sticky=tk.W, pady=(0, 8))
        
        self.delete_unused_var = tk.BooleanVar(value=False)
        self.delete_check = ttk.Checkbutton(
            self.delete_option_frame, 
            text="自动删除未使用资源（谨慎操作）", 
            variable=self.delete_unused_var
        )
        self.delete_check.pack(side=tk.LEFT)
        
        # 初始化显示状态
        self.on_analysis_type_change()
    
    def create_results_display(self, parent):
        """创建结果显示区域"""
        # 结果框架
        results_frame = ttk.Frame(parent)
        results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(8, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 结果文本区域
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            width=50, 
            height=8, 
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 初始提示文本
        self.results_text.insert(tk.END, "请选择项目目录并点击'开始分析'按钮\n")
        self.results_text.config(state=tk.DISABLED)
    
    def on_analysis_type_change(self):
        """处理分析类型变化"""
        analysis_type = self.analysis_type_var.get()
        
        if analysis_type == "clean":
            # 显示删除选项
            self.delete_option_frame.grid(row=3, column=0, sticky=tk.W, pady=(0, 8))
        else:
            # 隐藏删除选项
            self.delete_option_frame.grid_forget()
    
    def browse_project_directory(self):
        """浏览项目目录"""
        directory_path = filedialog.askdirectory(
            title="选择Cocos Creator项目资源目录",
            initialdir=self.project_dir_var.get() or os.getcwd()
        )
        
        if directory_path:
            self.project_dir_var.set(directory_path)
            # 自动生成输出文件路径
            self.generate_output_filename()
    
    def browse_output_file(self):
        """浏览输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=self.output_file_var.get() or "analysis_result.txt"
        )
        
        if file_path:
            self.output_file_var.set(file_path)
    
    def generate_output_filename(self):
        """自动生成输出文件名"""
        project_dir = self.project_dir_var.get()
        if not project_dir:
            return
        
        # 从项目目录名生成输出文件名
        project_name = os.path.basename(project_dir)
        analysis_type = self.analysis_type_var.get()
        
        if analysis_type == "clean":
            filename = f"{project_name}_unused_assets.txt"
        else:
            filename = f"{project_name}_asset_sizes.txt"
        
        # 放在项目目录的父目录中
        parent_dir = os.path.dirname(project_dir)
        output_path = os.path.join(parent_dir, filename)
        
        self.output_file_var.set(output_path)
    
    def run_analysis(self):
        """运行分析"""
        if self.is_processing:
            messagebox.showwarning("正在处理", "请等待当前分析完成")
            return
        
        # 获取参数
        project_dir = self.project_dir_var.get().strip()
        output_file = self.output_file_var.get().strip()
        analysis_type = self.analysis_type_var.get()
        
        # 验证参数
        if not project_dir:
            messagebox.showerror("参数错误", "请选择项目目录")
            return
        
        if not os.path.isdir(project_dir):
            messagebox.showerror("目录错误", "指定的项目目录不存在")
            return
        
        if not output_file:
            messagebox.showerror("参数错误", "请选择输出文件")
            return
        
        # 清空结果显示
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"开始分析...\n项目目录: {project_dir}\n")
        self.results_text.config(state=tk.DISABLED)
        
        # 在新线程中运行分析
        self.is_processing = True
        self.run_analysis_btn.config(state=tk.DISABLED)
        
        self.processing_thread = threading.Thread(
            target=self._run_analysis_thread,
            args=(project_dir, output_file, analysis_type)
        )
        self.processing_thread.start()
    
    def _run_analysis_thread(self, project_dir, output_file, analysis_type):
        """在线程中运行分析"""
        try:
            # 更新状态
            self._update_results(f"正在分析类型: {analysis_type}\n")
            self._update_results("正在扫描文件...\n")
            
            # 执行分析
            if analysis_type == "clean":
                delete_unused = self.delete_unused_var.get()
                self._update_results(f"删除未使用资源: {'是' if delete_unused else '否'}\n")
                clean_start(project_dir, output_file, delete_unused=delete_unused)
            else:
                size_start(project_dir, output_file)
            
            # 分析完成
            self._update_results(f"\n分析完成！结果已保存到:\n{output_file}\n")
            
            # 读取并显示结果
            if os.path.exists(output_file):
                self._update_results("\n--- 分析结果 ---\n")
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._update_results(content)
            
            # 滚动到最顶端
            self.parent.after(0, lambda: self.results_text.see(1.0))
            
            # 在主线程中显示完成消息
            self.parent.after(0, lambda: self.on_analysis_complete(output_file))
            
        except Exception as e:
            error_msg = f"分析过程中发生错误: {str(e)}"
            self._update_results(f"\n错误: {error_msg}\n")
            self.parent.after(0, lambda: self.on_analysis_error(error_msg))
        
        finally:
            self.is_processing = False
            self.parent.after(0, lambda: self.run_analysis_btn.config(state=tk.NORMAL))
    
    def _update_results(self, text):
        """更新结果显示（线程安全）"""
        def update():
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, text)
            self.results_text.see(tk.END)
            self.results_text.config(state=tk.DISABLED)
        
        self.parent.after(0, update)
    
    def on_analysis_complete(self, output_file):
        """分析完成时的回调"""
        messagebox.showinfo("分析完成", f"资源分析已完成！\n结果已保存到:\n{output_file}")
    
    def on_analysis_error(self, error_message):
        """分析错误时的回调"""
        messagebox.showerror("分析错误", f"分析过程中发生错误:\n{error_message}")