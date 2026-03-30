import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

def log_output(text_widget, message):
    """
    将日志信息输出到Text控件
    """
    text_widget.insert(tk.END, message + "\n")
    text_widget.yview(tk.END)  # 自动滚动到最后一行

def organize_images_by_prefix(cutai_image_path, result_root_dir, subfolder_name, text_widget):
    """
    按照图片文件名前缀分类整理文件，并将结果放到指定的结果根目录下
    """
    if not os.path.exists(cutai_image_path):
        log_output(text_widget, f"错误：路径 {cutai_image_path} 不存在")
        return 0
    
    files = os.listdir(cutai_image_path)
    prefix_files = {}

    for file in files:
        file_path = os.path.join(cutai_image_path, file)
        if os.path.isdir(file_path):
            continue
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            match = re.match(r'^([^_]+)_', file)
            if match:
                prefix = match.group(1)
                if prefix not in prefix_files:
                    prefix_files[prefix] = {'images': [], 'jsons': []}
                prefix_files[prefix]['images'].append(file)
                json_file = file.rsplit('.', 1)[0] + '.json'
                json_path = os.path.join(cutai_image_path, json_file)
                if os.path.exists(json_path):
                    prefix_files[prefix]['jsons'].append(json_file)
        elif file.lower().endswith('.json'):
            image_file = file.rsplit('.', 1)[0] + '.png'
            image_path = os.path.join(cutai_image_path, image_file)
            if os.path.exists(image_path):
                match = re.match(r'^([^_]+)_', file)
                if match:
                    prefix = match.group(1)
                    if prefix not in prefix_files:
                        prefix_files[prefix] = {'images': [], 'jsons': []}
                    if file not in prefix_files[prefix]['jsons']:
                        prefix_files[prefix]['jsons'].append(file)
                    if image_file not in prefix_files[prefix]['images']:
                        prefix_files[prefix]['images'].append(image_file)

    # 创建分类文件夹并复制文件
    for prefix, files_dict in prefix_files.items():
        target_dir = os.path.join(result_root_dir, prefix)
        os.makedirs(target_dir, exist_ok=True)
        
        log_output(text_widget, f"  创建分类文件夹: {prefix}")
        
        for image_file in files_dict['images']:
            src_path = os.path.join(cutai_image_path, image_file)
            dst_path = os.path.join(target_dir, image_file)
            try:
                shutil.copy2(src_path, dst_path)
                log_output(text_widget, f"    复制图片: {image_file}")
            except Exception as e:
                log_output(text_widget, f"    复制图片失败 {image_file}: {e}")
        
        for json_file in files_dict['jsons']:
            src_path = os.path.join(cutai_image_path, json_file)
            dst_path = os.path.join(target_dir, json_file)
            try:
                shutil.copy2(src_path, dst_path)
                log_output(text_widget, f"    复制JSON: {json_file}")
            except Exception as e:
                log_output(text_widget, f"    复制JSON失败 {json_file}: {e}")

    log_output(text_widget, f"  分类完成！共处理了 {len(prefix_files)} 个前缀类别")
    return len(prefix_files)

def process_all_subfolders(root_path, text_widget):
    """
    扫描根目录下的所有子文件夹，并找到 CutAIImage 文件夹进行分类整理
    """
    if not os.path.exists(root_path):
        log_output(text_widget, f"错误：根目录 {root_path} 不存在")
        return
    
    result_dir = os.path.join(root_path, "结果")
    os.makedirs(result_dir, exist_ok=True)
    
    total_processed = 0
    total_cutai_folders = 0
    total_dirs_scanned = 0
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d != "结果"]
        total_dirs_scanned += 1
        
        if "CutAIImage" in dirnames:
            cutai_path = os.path.join(dirpath, "CutAIImage")
            total_cutai_folders += 1
            subfolder_name = os.path.basename(dirpath) or "root"
            processed_count = organize_images_by_prefix(cutai_path, result_dir, subfolder_name, text_widget)
            total_processed += processed_count
    
    log_output(text_widget, "\n" + "=" * 60)
    log_output(text_widget, f"扫描完成！")
    log_output(text_widget, f"累计扫描目录数: {total_dirs_scanned}")
    log_output(text_widget, f"找到 {total_cutai_folders} 个CutAIImage文件夹")
    log_output(text_widget, f"共处理了 {total_processed} 个前缀类别")

def select_folder_and_process(text_widget):
    """
    选择根目录并批量处理所有子文件夹中的CutAIImage
    """
    root_path = filedialog.askdirectory(title="选择根目录")
    if root_path:
        process_all_subfolders(root_path, text_widget)

def select_single_folder_and_process(text_widget):
    """
    选择单个文件夹并处理
    """
    cutai_path = filedialog.askdirectory(title="选择CutAIImage文件夹")
    if cutai_path:
        result_dir = filedialog.askdirectory(title="选择结果保存目录")
        if not result_dir:
            result_dir = os.path.join(os.path.dirname(cutai_path), "结果")
        organize_images_by_prefix(cutai_path, result_dir, "单个文件夹", text_widget)

def create_gui():
    """
    创建GUI窗口
    """
    window = tk.Tk()
    window.title("图片分类整理工具")
    window.geometry("600x400")

    label = tk.Label(window, text="请选择处理模式", font=("Arial", 14))
    label.pack(pady=20)

    btn_single = tk.Button(window, text="处理单个CutAIImage文件夹", width=30, height=2, command=lambda: select_single_folder_and_process(log_text))
    btn_single.pack(pady=10)

    btn_batch = tk.Button(window, text="批量处理所有子文件夹中的CutAIImage", width=30, height=2, command=lambda: select_folder_and_process(log_text))
    btn_batch.pack(pady=10)

    log_text = tk.Text(window, height=10, width=70)
    log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # 修改为fill和expand选项，使日志窗口自动随主窗口变化

    scroll_y = tk.Scrollbar(window, orient="vertical", command=log_text.yview)
    log_text.config(yscrollcommand=scroll_y.set)
    scroll_y.pack(side="right", fill="y")

    window.mainloop()

if __name__ == "__main__":
    create_gui()
