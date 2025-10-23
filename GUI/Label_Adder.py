import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import shutil
from pathlib import Path
import re
import threading
import sys
from collections import defaultdict

# 设置标准输出编码为 UTF-8，兼容中文路径
if sys.stdout.encoding != 'UTF-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

class FileCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件复制工具")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # 初始化默认值
        self.source_dir = ""
        self.target_dir = ""
        self.target_labels = []
        self.all_labels = []  # 存储所有标签
        self.copy_times = 1
        self.start_seq = 1
        
        # 处理状态
        self.processing = False
        self.cancel_requested = False
        
        # 标签统计
        self.label_stats = defaultdict(int)
        self.label_total_counts = defaultdict(int)  # 存储标签总数
        self.label_copy_times = {}  # 存储每个标签的复制份数
        
        self.create_widgets()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建分割框架
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 配置框架
        config_frame = ttk.LabelFrame(paned_window, text="配置选项", padding=10)
        paned_window.add(config_frame, weight=1)
        
        # 源目录
        source_frame = ttk.Frame(config_frame)
        source_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        ttk.Label(source_frame, text="源目录:").grid(row=0, column=0, sticky=tk.W)
        self.source_dir_var = tk.StringVar()
        ttk.Entry(source_frame, textvariable=self.source_dir_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(source_frame, text="浏览...", command=self.browse_source_dir).grid(row=0, column=2)
        
        # 目标目录
        target_frame = ttk.Frame(config_frame)
        target_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        ttk.Label(target_frame, text="目标目录:").grid(row=0, column=0, sticky=tk.W)
        self.target_dir_var = tk.StringVar()
        ttk.Entry(target_frame, textvariable=self.target_dir_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(target_frame, text="浏览...", command=self.browse_target_dir).grid(row=0, column=2)
        
        # 标签框架
        label_frame = ttk.LabelFrame(config_frame, text="标签选择", padding=10)
        label_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)
        
        # 标签列表框架
        list_frame = ttk.Frame(label_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标签列表
        self.label_list = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=8)
        self.label_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.label_list.yview)
        self.label_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 标签操作按钮
        button_frame = ttk.Frame(label_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="加载标签", command=self.load_labels).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="全选", command=self.select_all_labels).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空选择", command=self.clear_label_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="设置复制份数", command=self.set_copy_times).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="预览标签数量", command=self.preview_label_counts).pack(side=tk.LEFT, padx=5)
        
        # 复制选项
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(options_frame, text="默认复制份数:").grid(row=0, column=0, sticky=tk.W)
        self.copy_times_var = tk.IntVar(value=1)
        ttk.Spinbox(options_frame, from_=1, to=100, width=5, textvariable=self.copy_times_var).grid(row=0, column=1, padx=5)
        
        ttk.Label(options_frame, text="起始序号:").grid(row=0, column=2, padx=(20, 0))
        self.start_seq_var = tk.IntVar(value=1)
        ttk.Spinbox(options_frame, from_=-1, to=10000, width=5, textvariable=self.start_seq_var).grid(row=0, column=3, padx=5)
        ttk.Label(options_frame, text="(-1表示自动计算)").grid(row=0, column=4, padx=5)
        
        # 操作按钮
        buttons_frame = ttk.Frame(config_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(buttons_frame, text="开始复制", command=self.start_copy)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = ttk.Button(buttons_frame, text="停止", command=self.stop_copy, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        progress_frame = ttk.Frame(config_frame)
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(progress_frame, text="进度:").grid(row=0, column=0, sticky=tk.W)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_frame = ttk.Frame(config_frame)
        status_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(status_frame, text="状态:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 日志框架
        log_frame = ttk.LabelFrame(paned_window, text="处理日志", padding=10)
        paned_window.add(log_frame, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # 配置权重
        config_frame.columnconfigure(1, weight=1)
        progress_frame.columnconfigure(1, weight=1)
        
    def browse_source_dir(self):
        dir_path = filedialog.askdirectory(title="选择源目录")
        if dir_path:
            self.source_dir_var.set(dir_path)
    
    def browse_target_dir(self):
        dir_path = filedialog.askdirectory(title="选择目标目录")
        if dir_path:
            self.target_dir_var.set(dir_path)
    
    def load_labels(self):
        """从源目录加载所有标签并显示数量"""
        source_dir = self.source_dir_var.get().strip()
        if not source_dir:
            messagebox.showerror("输入错误", "请先选择源目录")
            return
            
        try:
            # 清空当前标签列表
            self.label_list.delete(0, tk.END)
            self.all_labels = []
            self.label_total_counts.clear()
            
            # 收集所有标签和数量
            label_counts = defaultdict(int)
            total_files = 0
            total_annotations = 0
            
            for root, _, files in os.walk(source_dir):
                for f in files:
                    if f.lower().endswith('.json'):
                        total_files += 1
                        json_path = Path(root) / f
                        try:
                            with open(json_path, 'r', encoding='utf-8') as file:
                                data = json.load(file)
                            for shape in data.get('shapes', []):
                                label = shape.get('label', '').strip()
                                if label:
                                    label_counts[label] += 1
                                    total_annotations += 1
                        except Exception as e:
                            self.log_message(f"读取JSON失败 {json_path}: {str(e)}")
            
            # 保存标签总数
            self.label_total_counts = label_counts.copy()
            
            # 按标签名称排序
            sorted_labels = sorted(label_counts.items(), key=lambda x: x[0])
            
            # 添加到列表
            for label, count in sorted_labels:
                display_text = f"{label} ({count})"
                self.all_labels.append(label)
                self.label_list.insert(tk.END, display_text)
            
            # 显示统计信息
            unique_labels = len(label_counts)
            self.log_message(f"从源目录加载了 {unique_labels} 个唯一标签")
            self.log_message(f"总文件数: {total_files}")
            self.log_message(f"总标注实例数: {total_annotations}")
            
            # 显示标签分布
            if unique_labels > 0:
                self.log_message("标签分布:")
                for label, count in sorted_labels:
                    percentage = (count / total_annotations) * 100
                    self.log_message(f"  {label}: {count} ({percentage:.1f}%)")
            
        except Exception as e:
            messagebox.showerror("加载标签失败", f"加载标签时出错: {str(e)}")
    
    def select_all_labels(self):
        """选择所有标签"""
        self.label_list.selection_set(0, tk.END)
    
    def clear_label_selection(self):
        """清空标签选择"""
        self.label_list.selection_clear(0, tk.END)
    
    def get_selected_labels(self):
        """获取选中的标签（去除数量显示）"""
        selected_indices = self.label_list.curselection()
        selected_labels = []
        for i in selected_indices:
            # 从显示文本中提取标签名（去除括号和数量）
            display_text = self.label_list.get(i)
            label_name = display_text.split(' (')[0]  # 假设格式为"标签名 (数量)"
            selected_labels.append(label_name)
        return selected_labels
    
    def set_copy_times(self):
        """设置每个标签的复制份数"""
        selected_labels = self.get_selected_labels()
        if not selected_labels:
            messagebox.showwarning("警告", "请先选择标签")
            return
        
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置标签复制份数")
        settings_window.geometry("500x400")
        settings_window.resizable(True, True)
        
        # 主框架
        main_frame = ttk.Frame(settings_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="设置标签复制份数", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 说明
        note_label = ttk.Label(main_frame, text="为每个选中的标签设置复制份数（留空使用默认值）", 
                              font=("Arial", 9), foreground="gray")
        note_label.pack(pady=(0, 10))
        
        # 创建可滚动的框架
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加标签和输入框
        self.copy_entries = {}
        for i, label in enumerate(selected_labels):
            # 标签名称
            label_frame = ttk.Frame(scrollable_frame)
            label_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(label_frame, text=label, width=20).pack(side=tk.LEFT, padx=5)
            
            # 输入框
            entry_var = tk.StringVar()
            # 设置当前值（如果有）
            if label in self.label_copy_times:
                entry_var.set(str(self.label_copy_times[label]))
            
            entry = ttk.Entry(label_frame, textvariable=entry_var, width=10)
            entry.pack(side=tk.LEFT, padx=5)
            
            # 保存引用
            self.copy_entries[label] = entry_var
            
            # 默认值提示
            default_value = self.copy_times_var.get()
            ttk.Label(label_frame, text=f"(默认: {default_value})", foreground="gray").pack(side=tk.LEFT, padx=5)
        
        # 布局滚动区域
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 保存按钮
        def save_settings():
            # 收集设置
            for label, entry_var in self.copy_entries.items():
                value = entry_var.get().strip()
                if value:
                    try:
                        times = int(value)
                        if times < 1:
                            messagebox.showerror("输入错误", f"'{label}'的复制份数必须大于0")
                            return
                        self.label_copy_times[label] = times
                    except ValueError:
                        messagebox.showerror("输入错误", f"'{label}'的复制份数必须是整数")
                        return
                elif label in self.label_copy_times:
                    # 如果留空，则删除该标签的设置
                    del self.label_copy_times[label]
            
            # 显示设置结果
            result_text = "已设置复制份数的标签:\n"
            for label, times in self.label_copy_times.items():
                if label in selected_labels:
                    result_text += f"  {label}: {times}\n"
            
            if result_text == "已设置复制份数的标签:\n":
                result_text = "所有标签将使用默认复制份数"
            
            self.log_message(result_text)
            settings_window.destroy()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="保存", command=save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def preview_label_counts(self):
        """预览添加标签后的数量统计"""
        source_dir = self.source_dir_var.get().strip()
        target_labels = self.get_selected_labels()
        default_copy_times = self.copy_times_var.get()
        
        if not source_dir:
            messagebox.showerror("输入错误", "请先选择源目录")
            return
            
        if not target_labels:
            messagebox.showerror("输入错误", "请选择至少一个标签")
            return
        
        # 如果没有加载标签，则先加载
        if not self.label_total_counts:
            self.load_labels()
            if not self.label_total_counts:
                return
        
        # 在新线程中执行预览
        self.preview_thread = threading.Thread(
            target=self.calculate_label_counts,
            args=(source_dir, target_labels, default_copy_times),
            daemon=True
        )
        self.preview_thread.start()
    
    def calculate_label_counts(self, source_dir, target_labels, default_copy_times):
        """计算标签数量，与复制逻辑完全对应"""
        try:
            # 初始化统计
            label_current_counts = defaultdict(int)  # 当前标签数量
            label_future_counts = defaultdict(int)   # 复制后标签数量
            total_files = 0
            files_with_labels = 0
            
            # 收集所有JSON文件
            json_files = []
            for root, _, files in os.walk(source_dir):
                for f in files:
                    if f.lower().endswith('.json'):
                        json_files.append(Path(root) / f)
            
            total_files = len(json_files)
            processed_files = 0
            
            # 更新状态
            self.root.after(0, self.update_status, "正在统计标签数量...")
            
            for json_path in json_files:
                try:
                    # 读取JSON文件
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 检查是否包含目标标签
                    file_labels = set()
                    file_label_counts = defaultdict(int)  # 当前文件中每个标签的数量
                    
                    for shape in data.get('shapes', []):
                        label = shape.get('label', '')
                        if label in target_labels:
                            file_labels.add(label)
                            file_label_counts[label] += 1
                    
                    if not file_labels:
                        processed_files += 1
                        progress = (processed_files / total_files) * 100
                        self.root.after(0, self.update_progress, progress)
                        self.root.after(0, self.update_status, f"统计中: {processed_files}/{total_files} 文件")
                        continue
                    
                    # 确定此文件的复制份数（取所有标签中最大的复制份数）
                    file_copy_times = default_copy_times
                    for label in file_labels:
                        if label in self.label_copy_times:
                            file_copy_times = max(file_copy_times, self.label_copy_times[label])
                    
                    # 统计当前和复制后的标签数量
                    for label, count in file_label_counts.items():
                        label_current_counts[label] += count
                        label_future_counts[label] += count * file_copy_times
                    
                    files_with_labels += 1
                    processed_files += 1
                    progress = (processed_files / total_files) * 100
                    self.root.after(0, self.update_progress, progress)
                    self.root.after(0, self.update_status, f"统计中: {processed_files}/{total_files} 文件")
                    
                except Exception as e:
                    self.root.after(0, self.log_message, f"统计失败 {json_path}: {str(e)}")
                    continue
            
            # 显示统计结果
            self.root.after(0, self.show_label_counts, label_current_counts, label_future_counts, 
                           default_copy_times, total_files, files_with_labels)
            
        except Exception as e:
            self.root.after(0, self.handle_error, str(e))
    
    def show_label_counts(self, label_current_counts, label_future_counts, default_copy_times, total_files, files_with_labels):
        """显示标签数量统计"""
        # 创建新窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("标签数量预览")
        preview_window.geometry("600x500")
        preview_window.resizable(True, True)
        
        # 主框架
        main_frame = ttk.Frame(preview_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="标签数量统计", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 创建表格框架
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        columns = ("标签", "当前总数", "复制份数", "复制后总数", "增加比例")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER)
        
        # 添加数据
        total_current = 0
        total_future = 0
        
        for label in sorted(label_current_counts.keys()):
            current_count = label_current_counts[label]
            copy_times = self.label_copy_times.get(label, default_copy_times)
            future_count = label_future_counts[label]
            increase_ratio = f"{((future_count - current_count) / current_count * 100):.1f}%" if current_count > 0 else "N/A"
            
            tree.insert("", tk.END, values=(label, current_count, copy_times, future_count, increase_ratio))
            
            total_current += current_count
            total_future += future_count
        
        # 添加总计行
        total_increase_ratio = f"{((total_future - total_current) / total_current * 100):.1f}%" if total_current > 0 else "N/A"
        tree.insert("", tk.END, values=("总计", total_current, "", total_future, total_increase_ratio))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 汇总信息
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, pady=10)
        
        summary_text = (
            f"总文件数: {total_files}\n"
            f"包含选中标签的文件数: {files_with_labels}\n"
            f"默认复制份数: {default_copy_times}\n"
            f"预计总标签实例数: {total_current} → {total_future}"
        )
        
        summary_label = ttk.Label(summary_frame, text=summary_text, justify=tk.LEFT)
        summary_label.pack(anchor=tk.W)
        
        # 关闭按钮
        close_button = ttk.Button(main_frame, text="关闭", command=preview_window.destroy)
        close_button.pack(pady=10)
        
        # 重置进度条
        self.root.after(0, self.update_progress, 0)
        self.root.after(0, self.update_status, "就绪")
    
    def start_copy(self):
        if self.processing:
            return
            
        # 验证输入
        source_dir = self.source_dir_var.get().strip()
        target_dir = self.target_dir_var.get().strip()
        target_labels = self.get_selected_labels()
        default_copy_times = self.copy_times_var.get()
        start_seq = self.start_seq_var.get()
        
        if not source_dir:
            messagebox.showerror("输入错误", "请选择源目录")
            return
            
        if not target_dir:
            messagebox.showerror("输入错误", "请选择目标目录")
            return
            
        if not target_labels:
            messagebox.showerror("输入错误", "请选择至少一个标签")
            return
            
        # 更新UI状态
        self.processing = True
        self.cancel_requested = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("复制中...")
        self.progress_var.set(0)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"开始复制: 源目录={source_dir}\n")
        self.log_text.insert(tk.END, f"目标目录: {target_dir}\n")
        self.log_text.insert(tk.END, f"目标标签: {', '.join(target_labels)}\n")
        self.log_text.insert(tk.END, f"默认复制份数: {default_copy_times}\n")
        
        # 显示每个标签的复制份数
        if self.label_copy_times:
            self.log_text.insert(tk.END, "自定义复制份数:\n")
            for label, times in self.label_copy_times.items():
                if label in target_labels:
                    self.log_text.insert(tk.END, f"  {label}: {times}\n")
        
        self.log_text.insert(tk.END, f"起始序号: {'自动计算' if start_seq == -1 else start_seq}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
        
        # 启动复制线程
        self.copy_thread = threading.Thread(
            target=self.copy_labeled_files,
            args=(source_dir, target_dir, target_labels, default_copy_times, start_seq),
            daemon=True
        )
        self.copy_thread.start()
    
    def stop_copy(self):
        if self.processing:
            self.cancel_requested = True
            self.status_var.set("正在停止...")
    
    def update_progress(self, value):
        self.progress_var.set(value)
    
    def update_status(self, message):
        self.status_var.set(message)
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
    
    def copy_complete(self, total_copied, current_seq):
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(100)
        
        # 显示结果
        result = (
            f"\n复制完成！共复制 {total_copied} 个文件\n"
            f"最终序号: {current_seq - 1}\n"
            f"目标目录: {self.target_dir_var.get()}"
        )
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, result + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
        
        self.status_var.set("复制完成")
        messagebox.showinfo("复制完成", result)
    
    def handle_error(self, error):
        self.log_message(f"错误: {error}")
        self.status_var.set(f"错误: {error}")
        messagebox.showerror("复制错误", f"发生错误: {error}")
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def copy_labeled_files(self, source_dir, target_dir, target_labels, default_copy_times, start_seq):
        try:
            # 支持的图片格式
            img_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp')
            
            # 创建目标目录
            Path(target_dir).mkdir(parents=True, exist_ok=True)
            
            # 收集所有JSON文件
            json_files = []
            for root, _, files in os.walk(source_dir):
                for f in files:
                    if f.lower().endswith('.json'):
                        json_files.append(Path(root) / f)
            
            # 如果起始序号为-1，自动计算目标目录中最大序号
            current_seq = start_seq
            if start_seq == -1:
                max_seq = 0
                for file in Path(target_dir).iterdir():
                    if file.is_file() and file.suffix.lower() == '.json':
                        match = re.search(r'_(\d+)\.json$', file.name)
                        if match:
                            seq = int(match.group(1))
                            if seq > max_seq:
                                max_seq = seq
                current_seq = max_seq + 1
                self.log_message(f"自动计算起始序号: {current_seq}")
            
            total_files = len(json_files)
            processed_files = 0
            total_copied = 0
            
            # 更新初始进度
            self.root.after(0, self.update_progress, 0)
            self.root.after(0, self.update_status, f"处理中: 0/{total_files} 文件")
            
            for json_path in json_files:
                if self.cancel_requested:
                    break
                
                try:
                    # 读取JSON文件
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 检查是否包含目标标签
                    file_labels = set()
                    for shape in data.get('shapes', []):
                        label = shape.get('label', '')  # 修复：定义label变量
                        if label in target_labels:
                            file_labels.add(label)
                    
                    if not file_labels:
                        processed_files += 1
                        progress = (processed_files / total_files) * 100
                        self.root.after(0, self.update_progress, progress)
                        self.root.after(0, self.update_status, f"处理中: {processed_files}/{total_files} 文件")
                        continue
                    
                    # 查找对应的图片文件
                    img_path = None
                    for ext in img_exts:
                        possible_img = json_path.with_suffix(ext)
                        if possible_img.exists():
                            img_path = possible_img
                            break
                    
                    if not img_path:
                        self.log_message(f"警告：找不到 {json_path.stem} 的图片文件")
                        processed_files += 1
                        progress = (processed_files / total_files) * 100
                        self.root.after(0, self.update_progress, progress)
                        self.root.after(0, self.update_status, f"处理中: {processed_files}/{total_files} 文件")
                        continue
                    
                    # 获取原始文件名（不含扩展名）
                    base_stem = json_path.stem
                    
                    # 确定此文件的复制份数（取所有标签中最大的复制份数）
                    file_copy_times = default_copy_times
                    for label in file_labels:
                        if label in self.label_copy_times:
                            file_copy_times = max(file_copy_times, self.label_copy_times[label])
                    
                    # 复制指定份数
                    for i in range(file_copy_times):
                        # 直接在原文件名后添加序号
                        new_stem = f"{base_stem}_{i}"
                        new_json = f"{new_stem}.json"
                        new_img = f"{new_stem}{img_path.suffix}"
                        
                        # 新文件路径
                        new_json_path = Path(target_dir) / new_json
                        new_img_path = Path(target_dir) / new_img
                        
                        # 复制文件
                        shutil.copy2(json_path, new_json_path)
                        shutil.copy2(img_path, new_img_path)
                        
                        # 更新JSON中的图片路径
                        with open(new_json_path, 'r+', encoding='utf-8') as f:
                            json_data = json.load(f)
                            json_data['imagePath'] = new_img
                            f.seek(0)
                            json.dump(json_data, f, ensure_ascii=False, indent=2)
                            f.truncate()
                        
                        total_copied += 1
                        current_seq += 1  # 递增序号
                    
                    processed_files += 1
                    progress = (processed_files / total_files) * 100
                    self.root.after(0, self.update_progress, progress)
                    self.root.after(0, self.update_status, f"处理中: {processed_files}/{total_files} 文件")
                    self.root.after(0, self.log_message, f"已复制: {json_path.name} ({file_copy_times}份)")
                
                except Exception as e:
                    self.root.after(0, self.log_message, f"处理失败 {json_path}: {str(e)}")
                    continue
            
            # 复制完成
            self.root.after(0, self.copy_complete, total_copied, current_seq)
            
        except Exception as e:
            self.root.after(0, self.handle_error, str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopyApp(root)
    root.mainloop()