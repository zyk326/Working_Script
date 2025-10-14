import os
import shutil
import re
from pathlib import Path

def organize_images_by_prefix(cutai_image_path, result_root_dir, subfolder_name):
    """
    按照图片文件名前缀分类整理文件，并将结果放到指定的结果根目录下
    
    Args:
        cutai_image_path (str): CutAIImage文件夹的路径
        result_root_dir (str): 结果根目录路径
        subfolder_name (str): 子文件夹名称（用于区分不同来源）
    """
    
    # 检查路径是否存在
    if not os.path.exists(cutai_image_path):
        print(f"错误：路径 {cutai_image_path} 不存在")
        return 0
    
    # 获取所有文件
    files = os.listdir(cutai_image_path)
    
    
    # 分类存储文件
    prefix_files = {}
    
    for file in files:
        file_path = os.path.join(cutai_image_path, file)
        
        # 跳过文件夹
        if os.path.isdir(file_path):
            continue
            
        # 检查是否为图片文件
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            # 使用正则表达式提取前缀 (xx_yyyy.png 中的 xx 部分)
            match = re.match(r'^([^_]+)_', file)
            if match:
                prefix = match.group(1)
                
                if prefix not in prefix_files:
                    prefix_files[prefix] = {'images': [], 'jsons': []}
                
                prefix_files[prefix]['images'].append(file)
                
                # 检查是否有对应的JSON文件
                json_file = file.rsplit('.', 1)[0] + '.json'
                json_path = os.path.join(cutai_image_path, json_file)
                
                if os.path.exists(json_path):
                    prefix_files[prefix]['jsons'].append(json_file)
        
        # 检查是否为JSON文件
        elif file.lower().endswith('.json'):
            # 检查是否有对应的图片文件
            image_file = file.rsplit('.', 1)[0] + '.png'
            image_path = os.path.join(cutai_image_path, image_file)
            
            if os.path.exists(image_path):
                # 提取前缀
                match = re.match(r'^([^_]+)_', file)
                if match:
                    prefix = match.group(1)
                    
                    if prefix not in prefix_files:
                        prefix_files[prefix] = {'images': [], 'jsons': []}
                    
                    # 避免重复添加
                    if file not in prefix_files[prefix]['jsons']:
                        prefix_files[prefix]['jsons'].append(file)
                    if image_file not in prefix_files[prefix]['images']:
                        prefix_files[prefix]['images'].append(image_file)
    
    # 创建分类文件夹并复制文件到结果目录
    for prefix, files_dict in prefix_files.items():
        # 在结果根目录下创建分类文件夹
        target_dir = os.path.join(result_root_dir, prefix)
        os.makedirs(target_dir, exist_ok=True)
        
        print(f"  创建分类文件夹: {prefix}")
        
        # 复制图片文件到结果目录
        for image_file in files_dict['images']:
            src_path = os.path.join(cutai_image_path, image_file)
            dst_path = os.path.join(target_dir, image_file)
            
            try:
                shutil.copy2(src_path, dst_path)  # 使用copy2保留文件元数据
                print(f"    复制图片: {image_file}")
            except Exception as e:
                print(f"    复制图片失败 {image_file}: {e}")
        
        # 复制JSON文件到结果目录
        for json_file in files_dict['jsons']:
            src_path = os.path.join(cutai_image_path, json_file)
            dst_path = os.path.join(target_dir, json_file)
            
            try:
                shutil.copy2(src_path, dst_path)  # 使用copy2保留文件元数据
                print(f"    复制JSON: {json_file}")
            except Exception as e:
                print(f"    复制JSON失败 {json_file}: {e}")
    
    print(f"  分类完成！共处理了 {len(prefix_files)} 个前缀类别")
    return len(prefix_files)

def process_all_subfolders(root_path):
    """
    遍历根目录下的所有嵌套子文件夹，找到任意层级的 CutAIImage 文件夹并进行分类整理
    将所有结果统一放到根目录下的"结果"文件夹中
    
    Args:
        root_path (str): 根目录路径
    """
    
    if not os.path.exists(root_path):
        print(f"错误：根目录 {root_path} 不存在")
        return
    
    print(f"开始扫描根目录(递归): {root_path}")
    print("=" * 60)
    
    # 创建结果文件夹
    result_dir = os.path.join(root_path, "结果")
    os.makedirs(result_dir, exist_ok=True)
    print(f"创建结果文件夹: {result_dir}")
    
    total_processed = 0
    total_cutai_folders = 0
    total_dirs_scanned = 0
    
    # 递归遍历所有层级
    for dirpath, dirnames, filenames in os.walk(root_path):
        # 跳过结果文件夹以避免自包含
        dirnames[:] = [d for d in dirnames if d != "结果"]
        total_dirs_scanned += 1
        
        # 检查当前目录是否包含 CutAIImage
        if "CutAIImage" in dirnames:
            cutai_path = os.path.join(dirpath, "CutAIImage")
            print(f"  找到CutAIImage文件夹: {cutai_path}")
            total_cutai_folders += 1
            # 使用所在上级目录名作为 subfolder_name
            subfolder_name = os.path.basename(dirpath) or "root"
            processed_count = organize_images_by_prefix(cutai_path, result_dir, subfolder_name)
            total_processed += processed_count
    
    print("\n" + "=" * 60)
    print(f"扫描完成！")
    print(f"累计扫描目录数: {total_dirs_scanned}")
    print(f"找到 {total_cutai_folders} 个CutAIImage文件夹")
    print(f"总共处理了 {total_processed} 个前缀类别")
    print(f"所有分类结果已保存到: {result_dir}")

def main():
    """主函数"""
    print("图片文件分类整理工具")
    print("=" * 50)
    
    # 选择处理模式
    print("请选择处理模式：")
    print("1. 处理单个CutAIImage文件夹")
    print("2. 批量处理根目录下的所有子文件夹中的CutAIImage")
    
    while True:
        choice = input("请输入选择 (1 或 2): ").strip()
        
        if choice == "1":
            # 模式1：处理单个CutAIImage文件夹
            process_single_folder()
            break
        elif choice == "2":
            # 模式2：批量处理所有子文件夹
            process_batch_folders()
            break
        else:
            print("无效选择，请输入 1 或 2")

def process_single_folder():
    """处理单个CutAIImage文件夹"""
    print("\n=== 模式1：处理单个CutAIImage文件夹 ===")
    
    # 获取用户输入的路径
    while True:
        path_input = input("请输入CutAIImage文件夹的完整路径 (或按回车使用当前目录): ").strip()
        
        if not path_input:
            # 使用当前目录
            current_dir = os.getcwd()
            cutai_path = os.path.join(current_dir, "CutAIImage")
            
            if os.path.exists(cutai_path):
                print(f"使用路径: {cutai_path}")
                break
            else:
                print(f"当前目录下未找到CutAIImage文件夹")
                print(f"当前目录: {current_dir}")
                continue
        
        elif os.path.exists(path_input):
            cutai_path = path_input
            break
        else:
            print(f"路径不存在: {path_input}")
            continue
    
    # 获取结果目录路径
    result_dir = input("请输入结果保存目录路径 (或按回车使用CutAIImage同级目录下的'结果'文件夹): ").strip()
    if not result_dir:
        # 使用CutAIImage同级目录下的"结果"文件夹
        cutai_parent = os.path.dirname(cutai_path)
        result_dir = os.path.join(cutai_parent, "结果")
    
    # 创建结果目录
    os.makedirs(result_dir, exist_ok=True)
    print(f"结果将保存到: {result_dir}")
    
    # 确认操作
    print(f"\n即将整理文件夹: {cutai_path}")
    print("此操作将按照图片文件名前缀创建分类文件夹并复制文件到结果目录")
    
    confirm = input("确认继续吗？(y/N): ").strip().lower()
    if confirm in ['y', 'yes', '是']:
        organize_images_by_prefix(cutai_path, result_dir, "单个文件夹")
    else:
        print("操作已取消")

def process_batch_folders():
    """批量处理根目录下的所有子文件夹"""
    print("\n=== 模式2：批量处理所有子文件夹 ===")
    
    # 获取用户输入的根目录路径
    while True:
        path_input = input("请输入根目录的完整路径 (或按回车使用当前目录): ").strip()
        
        if not path_input:
            # 使用当前目录
            root_path = os.getcwd()
            print(f"使用当前目录: {root_path}")
            break
        
        elif os.path.exists(path_input):
            root_path = path_input
            break
        else:
            print(f"路径不存在: {path_input}")
            continue
    
    # 确认操作
    print(f"\n即将扫描根目录: {root_path}")
    print("此操作将递归遍历所有子文件夹，找到任意层级的 CutAIImage 并进行分类整理")
    
    confirm = input("确认继续吗？(y/N): ").strip().lower()
    if confirm in ['y', 'yes', '是']:
        process_all_subfolders(root_path)
    else:
        print("操作已取消")

if __name__ == "__main__":
    main() 