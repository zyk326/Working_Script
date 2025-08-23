#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
钢网毛刺图片筛选工具 v2.0

扫描指定路径下的所有文件夹，找到包含"钢网毛刺"标签的图片和JSON文件，
找到后立即复制到目标文件夹的result子文件夹中（找到一个，复制一个）。

使用方法：直接修改代码中的路径配置，然后运行脚本即可。
"""

import os
import json
import shutil

# ==================== 配置区域 ====================
# 在这里修改你的路径配置

# 源路径：包含多个文件夹的根目录
SOURCE_PATH = r"Y:\2_标注数据\2025-05-10领益东莞  B788 Nozzle Mesh\C2"  # 修改为你的源路径

# 目标路径：结果将保存到该路径下的result文件夹
TARGET_PATH = r"Y:\2_标注数据\2025-05-10领益东莞  B788 Nozzle Mesh\result"    # 修改为你的目标路径

# 要筛选的标签名称
TARGET_LABEL = "钢网毛刺"   # 可以修改为其他标签

# 是否启用试运行模式（True=只预览不复制，False=实际复制）
DRY_RUN = False

# ==================== 配置区域结束 ====================


def find_and_copy_files_with_label(source_path: str, target_label: str, target_path: str, dry_run: bool = False) -> int:
    """
    在指定路径下递归查找包含目标标签的JSON文件，找到后立即复制
    
    Args:
        source_path: 源路径
        target_label: 目标标签名称
        target_path: 目标路径
        dry_run: 是否为试运行模式
        
    Returns:
        成功复制的文件对数
    """
    copied_count = 0
    
    print(f"正在扫描路径: {source_path}")
    print("=" * 60)
    
    # 创建result文件夹
    result_dir = os.path.join(target_path, "result")
    if not dry_run:
        os.makedirs(result_dir, exist_ok=True)
        print(f"创建目标文件夹: {result_dir}")
    else:
        print(f"试运行模式：将创建目标文件夹: {result_dir}")
    
    print("开始查找并复制文件...")
    print("=" * 60)
    
    # 遍历所有子文件夹
    for root, dirs, files in os.walk(source_path):
        # 跳过目标文件夹，避免无限递归
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'result']
        
        for file in files:
            if file.lower().endswith('.json'):
                json_path = os.path.join(root, file)
                
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 检查shapes下的label是否包含目标标签
                    if 'shapes' in data:
                        for shape in data['shapes']:
                            if 'label' in shape and target_label in shape['label']:
                                # 找到匹配的标签，检查对应的图片文件
                                image_name = data.get('imagePath', '')
                                if image_name:
                                    # 构建图片文件的完整路径
                                    image_path = os.path.join(root, image_name)
                                    
                                    if os.path.exists(image_path):
                                        # 立即复制文件
                                        copied = copy_single_file_pair(json_path, image_path, result_dir, dry_run)
                                        if copied:
                                            copied_count += 1
                                            print(f"✓ 已复制第 {copied_count} 对文件")
                                        print()
                                    else:
                                        print(f"警告：JSON文件存在但对应图片不存在: {image_path}")
                                
                                break  # 找到一个匹配的标签就够了
                                
                except json.JSONDecodeError as e:
                    print(f"警告：无法解析JSON文件 {json_path}: {e}")
                except Exception as e:
                    print(f"警告：处理文件 {json_path} 时出错: {e}")
    
    return copied_count


def copy_single_file_pair(json_path: str, image_path: str, result_dir: str, dry_run: bool = False) -> bool:
    """
    复制单个文件对（JSON + 图片）
    
    Args:
        json_path: JSON文件路径
        image_path: 图片文件路径
        result_dir: 目标文件夹
        dry_run: 是否为试运行模式
        
    Returns:
        是否复制成功
    """
    # 获取文件名
    json_name = os.path.basename(json_path)
    image_name = os.path.basename(image_path)
    
    # 目标路径
    target_json = os.path.join(result_dir, json_name)
    target_image = os.path.join(result_dir, image_name)
    
    if dry_run:
        print(f"试运行：将复制 {json_name} 和 {image_name}")
        return True
    
    try:
        # 复制JSON文件
        shutil.copy2(json_path, target_json)
        print(f"✓ 复制JSON: {json_name}")
        
        # 复制图片文件
        shutil.copy2(image_path, target_image)
        print(f"✓ 复制图片: {image_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ 复制失败 {json_name}/{image_name}: {e}")
        return False


def main():
    """主函数"""
    print("钢网毛刺图片筛选工具 v2.0")
    print("=" * 50)
    print(f"源路径: {SOURCE_PATH}")
    print(f"目标路径: {TARGET_PATH}")
    print(f"目标标签: {TARGET_LABEL}")
    print(f"试运行模式: {'是' if DRY_RUN else '否'}")
    print()
    
    # 检查源路径是否存在
    if not os.path.exists(SOURCE_PATH):
        print(f"错误：源路径不存在: {SOURCE_PATH}")
        print("请在代码中修改 SOURCE_PATH 为正确的路径")
        return
    
    # 检查目标路径是否存在，不存在则创建
    if not os.path.exists(TARGET_PATH):
        try:
            os.makedirs(TARGET_PATH, exist_ok=True)
            print(f"创建目标路径: {TARGET_PATH}")
        except Exception as e:
            print(f"错误：无法创建目标路径 {TARGET_PATH}: {e}")
            print("请在代码中修改 TARGET_PATH 为正确的路径")
            return
    
    # 查找并复制包含目标标签的文件（找到一个，复制一个）
    copied_count = find_and_copy_files_with_label(SOURCE_PATH, TARGET_LABEL, TARGET_PATH, DRY_RUN)
    
    if copied_count == 0:
        print("未找到包含目标标签的文件")
        return
    
    if not DRY_RUN:
        print("=" * 60)
        print(f"复制完成！成功复制了 {copied_count} 对文件")
        print(f"结果保存在: {os.path.join(TARGET_PATH, 'result')}")
    else:
        print("=" * 60)
        print("试运行完成！")
        print(f"将复制 {copied_count} 对文件到: {os.path.join(TARGET_PATH, 'result')}")
        print("如需实际复制，请将 DRY_RUN 设置为 False")


if __name__ == "__main__":
    main() 