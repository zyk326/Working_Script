#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ONNX 类别查看与修改工具 (GUI版)
作者: ChatGPT 优化版
功能:
  - 可视化读取 YOLO 导出的 ONNX 模型中类别名称 (metadata.names)
  - 支持修改类别名称并保存为新模型
  - 可通过按钮选择 ONNX 文件路径
  - 自动对齐布局 + 彩色按钮
"""

import os
import onnx
import ast
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


# ==================== 核心逻辑 ====================
def get_class_names_from_onnx(onnx_path, log=None):
    try:
        model = onnx.load(onnx_path)
        meta = {prop.key: prop.value for prop in model.metadata_props}
    except Exception as e:
        if log: log(f"❌ 读取模型失败: {e}")
        return None

    if "names" in meta:
        try:
            names_dict = ast.literal_eval(meta["names"])
            if log:
                log("✅ 检测到类别信息:")
                for idx, name in names_dict.items():
                    log(f"  编号 {idx}: {name}")
            return names_dict
        except Exception as e:
            if log:
                log(f"❌ 解析 names 失败: {e}")
                log(f"原始 names 内容: {meta['names']}")
            return None
    else:
        if log:
            log(f"⚠️ 模型 metadata 中未找到 'names'")
            log(f"可用 metadata keys: {list(meta.keys())}")
        return None


def modify_class_names_in_onnx(onnx_path, output_path, new_names_dict, log=None):
    try:
        model = onnx.load(onnx_path)
        new_names_str = str(new_names_dict)

        found = False
        for prop in model.metadata_props:
            if prop.key == "names":
                prop.value = new_names_str
                found = True
                break
        if not found:
            model.metadata_props.append(
                onnx.StringStringEntryProto(key="names", value=new_names_str)
            )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        onnx.save(model, output_path)
        if log:
            log(f"✅ 模型已保存到: {output_path}")
            log(f"新的类别信息: {new_names_dict}")
        return True
    except Exception as e:
        if log:
            log(f"❌ 修改失败: {e}")
        return False


# ==================== GUI 界面 ====================
class OnnxClassEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 ONNX 类别查看与修改工具")
        self.root.geometry("950x600")

        # 居中显示窗口
        self.root.update_idletasks()
        w, h = 950, 600
        ws, hs = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(ws - w)//2}+{(hs - h)//2}")

        # 背景与字体
        self.root.configure(bg="#f8f9fa")
        font_label = ("Microsoft YaHei", 10)
        pad_x = 8
        pad_y = 6

        # ==================== 路径输入部分 ====================
        frm_paths = tk.Frame(root, bg="#f8f9fa")
        frm_paths.pack(fill="x", pady=10, padx=15)

        tk.Label(frm_paths, text="ONNX 模型路径:", font=font_label, bg="#f8f9fa").grid(row=0, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.entry_onnx = tk.Entry(frm_paths, width=80)
        self.entry_onnx.grid(row=0, column=1, sticky="w", padx=pad_x)
        tk.Button(frm_paths, text="选择文件", command=self.select_onnx_file, width=12, bg="#1976D2", fg="white").grid(row=0, column=2, padx=pad_x)

        tk.Label(frm_paths, text="保存路径:", font=font_label, bg="#f8f9fa").grid(row=1, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.entry_output = tk.Entry(frm_paths, width=80)
        self.entry_output.grid(row=1, column=1, sticky="w", padx=pad_x)
        tk.Button(frm_paths, text="浏览", command=self.select_output, width=12, bg="#1976D2", fg="white").grid(row=1, column=2, padx=pad_x)

        # ==================== 类别编辑区 ====================
        frm_classes = tk.Frame(root, bg="#f8f9fa")
        frm_classes.pack(fill="x", pady=10, padx=15)

        tk.Label(frm_classes, text="类别字典 (格式 {0:'缺陷A',1:'缺陷B'}):", font=font_label, bg="#f8f9fa").grid(row=0, column=0, sticky="ne", padx=pad_x)
        self.text_new_names = scrolledtext.ScrolledText(frm_classes, width=78, height=6, font=("Consolas", 10))
        self.text_new_names.grid(row=0, column=1, columnspan=2, sticky="w", padx=pad_x)

        # ==================== 日志输出 ====================
        frm_log = tk.Frame(root, bg="#f8f9fa")
        frm_log.pack(fill="both", expand=True, pady=10, padx=15)

        tk.Label(frm_log, text="日志输出:", font=font_label, bg="#f8f9fa").grid(row=0, column=0, sticky="ne", padx=pad_x)
        self.text_log = scrolledtext.ScrolledText(frm_log, width=110, height=18, font=("Consolas", 10), bg="#1e1e1e", fg="#dcdcdc", insertbackground="white")
        self.text_log.grid(row=0, column=1, columnspan=2, sticky="w", padx=pad_x, pady=pad_y)

        # ==================== 按钮区 ====================
        frm_btn = tk.Frame(root, bg="#f8f9fa")
        frm_btn.pack(pady=10)
        tk.Button(frm_btn, text="🔍 查看类别", command=self.show_classes, bg="#2196F3", fg="white", width=14).pack(side="left", padx=8)
        tk.Button(frm_btn, text="📋 生成模板", command=self.generate_template, bg="#FFC107", fg="black", width=14).pack(side="left", padx=8)
        tk.Button(frm_btn, text="💾 修改并保存", command=self.modify_classes, bg="#4CAF50", fg="white", width=14).pack(side="left", padx=8)

    # ==================== 文件操作 ====================
    def select_onnx_file(self):
        path = filedialog.askopenfilename(title="选择 ONNX 文件", filetypes=[("ONNX 模型", "*.onnx")])
        if path:
            self.entry_onnx.delete(0, tk.END)
            self.entry_onnx.insert(0, path)

    def select_output(self):
        path = filedialog.asksaveasfilename(title="选择保存路径", defaultextension=".onnx", filetypes=[("ONNX 模型", "*.onnx")])
        if path:
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, path)

    # ==================== 日志 ====================
    def log(self, msg):
        self.text_log.configure(state="normal")
        self.text_log.insert(tk.END, msg + "\n")
        self.text_log.see(tk.END)
        self.text_log.configure(state="disabled")
        self.root.update()

    # ==================== 按钮功能 ====================
    def show_classes(self):
        path = self.entry_onnx.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("错误", "请选择有效的 ONNX 文件")
            return
        self.text_log.configure(state="normal")
        self.text_log.delete(1.0, tk.END)
        self.text_log.configure(state="disabled")
        self.log(f"读取模型: {path}")
        self.log("="*80)
        get_class_names_from_onnx(path, self.log)
        self.log("="*80)

    def generate_template(self):
        path = self.entry_onnx.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("错误", "请选择有效的 ONNX 文件")
            return
        names_dict = get_class_names_from_onnx(path)
        if names_dict is None:
            messagebox.showwarning("提示", "无法读取原始类别信息")
            return
        self.text_new_names.delete("1.0", tk.END)
        self.text_new_names.insert(tk.END, str(names_dict))
        self.log("📋 已生成原始类别模板到输入框")

    def modify_classes(self):
        onnx_path = self.entry_onnx.get().strip()
        output_path = self.entry_output.get().strip()
        new_text = self.text_new_names.get("1.0", tk.END).strip()

        if not onnx_path or not os.path.isfile(onnx_path):
            messagebox.showerror("错误", "请选择有效的 ONNX 文件")
            return
        if not output_path:
            messagebox.showerror("错误", "请指定保存路径")
            return
        if not new_text:
            messagebox.showerror("错误", "请输入新的类别字典")
            return

        try:
            new_names = ast.literal_eval(new_text)
            if not isinstance(new_names, dict):
                raise ValueError("输入的不是字典格式")
        except Exception as e:
            messagebox.showerror("错误", f"解析类别字典失败: {e}")
            return

        self.text_log.configure(state="normal")
        self.text_log.delete(1.0, tk.END)
        self.text_log.configure(state="disabled")

        self.log(f"开始修改模型: {onnx_path}")
        self.log(f"输出路径: {output_path}")
        self.log(f"新类别字典: {new_names}")
        self.log("="*80)

        current = get_class_names_from_onnx(onnx_path, self.log)
        if current is None:
            self.log("❌ 无法读取原始类别信息，终止操作。")
            return

        if len(new_names) != len(current):
            self.log(f"⚠️ 新类别数量 ({len(new_names)}) 与原始类别数量 ({len(current)}) 不匹配！")
            if not messagebox.askyesno("警告", "类别数量不匹配，是否继续保存？"):
                self.log("❌ 用户取消保存。")
                return

        success = modify_class_names_in_onnx(onnx_path, output_path, new_names, self.log)
        if success:
            self.log("="*80)
            self.log("✅ 修改完成，验证修改结果：")
            get_class_names_from_onnx(output_path, self.log)
        else:
            self.log("❌ 修改失败。")


if __name__ == "__main__":
    root = tk.Tk()
    app = OnnxClassEditor(root)
    root.mainloop()