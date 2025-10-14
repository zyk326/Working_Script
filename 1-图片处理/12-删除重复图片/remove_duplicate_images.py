#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除误复制的重复图片
例如：保留 G1_20250830191306412_4.jpg
      删除 G1_20250830191306412_4(2).jpg
"""

import os
import re
from pathlib import Path

# ===================== 配置区域 =====================
# 需要处理的目录（支持多个）
DIRECTORIES = [
    # r"D:\dataset\images",   # 示例路径1
    # r"D:\dataset\labels"    # 示例路径2
    r"U:/原始数据/2025-04-03领益 东莞  B25 SIM tool 卡针外观检测/2025-09-04-新增缺陷取图/内侧压伤NG100pcs/G/G1",
    r"U:/原始数据/2025-04-03领益 东莞  B25 SIM tool 卡针外观检测/2025-09-04-新增缺陷取图/内侧压伤NG100pcs/G/G2",
    r"U:/原始数据/2025-04-03领益 东莞  B25 SIM tool 卡针外观检测/2025-09-04-新增缺陷取图/内侧压伤NG100pcs/G/G3",
    r"U:/原始数据/2025-04-03领益 东莞  B25 SIM tool 卡针外观检测/2025-09-04-新增缺陷取图/内侧压伤NG100pcs/G/G4",
]

# 是否为试运行（True = 只打印将删除的文件，不真正删除）
DRY_RUN = False

# 支持的图片格式
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
# ====================================================


def is_duplicate_file(filename: str) -> bool:
    """
    判断文件名是否带有 (数字) 的重复标记
    """
    return re.search(r"\(\d+\)\.[^.]+$", filename) is not None


def remove_duplicates_in_dir(directory: Path):
    """
    删除指定目录下的重复图片
    """
    deleted_count = 0

    for file in directory.rglob("*"):
        if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
            if is_duplicate_file(file.name):
                if DRY_RUN:
                    print(f"[试运行] 将删除: {file}")
                else:
                    try:
                        file.unlink()
                        print(f"[已删除] {file}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"[错误] 删除失败 {file}: {e}")

    return deleted_count


def main():
    total_deleted = 0
    for path_str in DIRECTORIES:
        directory = Path(path_str)
        if not directory.exists():
            print(f"[警告] 路径不存在: {directory}")
            continue
        if not directory.is_dir():
            print(f"[警告] 不是目录: {directory}")
            continue

        print(f"\n=== 处理目录: {directory} ===")
        deleted_count = remove_duplicates_in_dir(directory)
        total_deleted += deleted_count

    print("\n========== 处理完成 ==========")
    print(f"总共删除了 {total_deleted} 个文件")
    if DRY_RUN:
        print("⚠ 当前为试运行模式，没有实际删除文件")


if __name__ == "__main__":
    main()
