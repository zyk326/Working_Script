#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件夹前缀移动工具 - GUI版
作者: ChatGPT
说明:
  - 扫描指定路径下的所有子文件夹，找到带有特定前缀的文件夹，
    并将其移动到目标路径中，保留原始结构。
  - 支持试运行（Dry Run）模式，仅显示不实际移动。
"""

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path


def move_single_folder(source_path: str, target_path: str, dry_run: bool = False, log=None) -> bool:
    """移动单个文件夹"""
    folder_name = os.path.basename(source_path)
    try:
        if dry_run:
            if log: log(f"🟡 试运行：{folder_name}")
            return True

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
            if log: log(f"⚠️ 已删除已存在目标: {target_path}")

        shutil.move(source_path, target_path)
        if log: log(f"✅ 移动成功: {source_path} -> {target_path}")
        return True
    except Exception as e:
        if log: log(f"❌ 移动失败 {folder_name}: {e}")
        return False


def find_and_move_prefix_folders(process_path, target_path, prefix, dry_run, log=None):
    """递归查找并移动"""
    moved_count = 0
    process_abs = os.path.abspath(process_path)
    target_abs = os.path.abspath(target_path)

    for root, dirs, files in os.walk(process_abs):
        root_abs = os.path.abspath(root)
        if root_abs.startswith(target_abs):
            continue
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for dir_name in dirs[:]:
            if dir_name.startswith(prefix):
                source_folder_path = os.path.join(root, dir_name)
                relative_path = os.path.relpath(root, process_abs)
                if relative_path == ".":
                    target_folder_path = os.path.join(target_path, dir_name)
                else:
                    target_folder_path = os.path.join(target_path, relative_path, dir_name)

                success = move_single_folder(source_folder_path, target_folder_path, dry_run, log)
                if success:
                    moved_count += 1
                    if log: log(f"✅ 已处理第 {moved_count} 个: {source_folder_path}")
                dirs.remove(dir_name)

    return moved_count


# ==================== GUI部分 ====================

class FolderMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📦 文件夹前缀移动工具")
        self.root.geometry("800x600")

        # 输入框与按钮
        tk.Label(root, text="扫描路径:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_process = tk.Entry(root, width=80)
        self.entry_process.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="选择", command=self.select_process_path).grid(row=0, column=2, padx=5)

        tk.Label(root, text="目标路径:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_target = tk.Entry(root, width=80)
        self.entry_target.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="选择", command=self.select_target_path).grid(row=1, column=2, padx=5)

        tk.Label(root, text="文件夹前缀:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_prefix = tk.Entry(root, width=20)
        self.entry_prefix.grid(row=2, column=1, sticky="w", padx=5)

        self.dry_run_var = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="试运行模式（不实际移动）", variable=self.dry_run_var).grid(row=2, column=1, sticky="e")

        # 日志显示
        tk.Label(root, text="日志输出:").grid(row=3, column=0, sticky="ne", padx=5)
        self.text_log = scrolledtext.ScrolledText(root, width=100, height=25, state="disabled")
        self.text_log.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

        # 操作按钮
        tk.Button(root, text="开始执行", command=self.start_move, bg="#4CAF50", fg="white").grid(row=4, column=1, pady=10)

    def select_process_path(self):
        path = filedialog.askdirectory(title="选择扫描路径")
        if path:
            self.entry_process.delete(0, tk.END)
            self.entry_process.insert(0, path)

    def select_target_path(self):
        path = filedialog.askdirectory(title="选择目标路径")
        if path:
            self.entry_target.delete(0, tk.END)
            self.entry_target.insert(0, path)

    def log(self, msg):
        self.text_log.configure(state="normal")
        self.text_log.insert(tk.END, msg + "\n")
        self.text_log.see(tk.END)
        self.text_log.configure(state="disabled")
        self.root.update()

    def start_move(self):
        process_path = self.entry_process.get().strip()
        target_path = self.entry_target.get().strip()
        prefix = self.entry_prefix.get().strip()
        dry_run = self.dry_run_var.get()

        if not process_path or not os.path.exists(process_path):
            messagebox.showerror("错误", "扫描路径不存在")
            return
        if not target_path:
            messagebox.showerror("错误", "目标路径不能为空")
            return
        if not prefix:
            messagebox.showerror("错误", "请填写文件夹前缀")
            return

        os.makedirs(target_path, exist_ok=True)
        self.text_log.configure(state="normal")
        self.text_log.delete(1.0, tk.END)
        self.text_log.configure(state="disabled")

        self.log(f"开始执行，扫描路径: {process_path}")
        self.log(f"目标路径: {target_path}")
        self.log(f"文件夹前缀: {prefix}")
        self.log(f"试运行模式: {'是' if dry_run else '否'}")
        self.log("=" * 70)

        moved_count = find_and_move_prefix_folders(process_path, target_path, prefix, dry_run, self.log)

        self.log("=" * 70)
        if moved_count == 0:
            self.log("⚠️ 未找到带有指定前缀的文件夹。")
        else:
            if dry_run:
                self.log(f"✅ 试运行完成！将移动 {moved_count} 个文件夹。")
            else:
                self.log(f"🎉 移动完成！成功移动 {moved_count} 个文件夹。")
        self.log("任务结束。")


if __name__ == "__main__":
    root = tk.Tk()
    app = FolderMoverApp(root)
    root.mainloop()
