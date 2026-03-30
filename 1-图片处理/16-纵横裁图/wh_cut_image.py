#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量纵横裁图脚本 (支持中文路径)
支持递归扫描多个路径，处理符合条件的文件夹（大写字母+数字）
"""

import os
import re
import cv2
import numpy as np

####################################
# 配置区域
####################################

# 要处理的多个路径
INPUT_PATHS = [
    r"C:\Users\Administrator\Desktop\B25\内侧压伤\内侧压伤",
    # r"16-纵横裁图/路径2"
]

# 处理方式: "width" -> 按宽裁切拼接, "height" -> 按高裁切拼接
PROCESS_MODE = "width"   # 可选: "width" / "height"
# PROCESS_MODE = "height"   # 可选: "width" / "height"

# 文件夹命名匹配规则：大写字母+数字
FOLDER_PATTERN = r"^[A-Z]\d+$"

# 支持的图片格式py
IMG_EXTS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]

####################################
# 工具函数
####################################

def imread_unicode(path):
    """解决 OpenCV 不支持中文路径的问题"""
    try:
        stream = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(stream, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"[ERROR] 读取失败: {path}, {e}")
        return None

def imwrite_unicode(path, img):
    """解决 OpenCV 不支持中文路径写入的问题"""
    ext = os.path.splitext(path)[1]
    _, buf = cv2.imencode(ext, img)
    buf.tofile(path)

####################################
# 处理逻辑
####################################

def process_image(img_path, mode):
    """按指定模式处理单张图片"""
    img = imread_unicode(img_path)
    if img is None:
        print(f"[WARN] 无法读取图片: {img_path}")
        return None

    h, w = img.shape[:2]

    if mode == "width":
        mid = w // 2
        left = img[:, :mid]
        right = img[:, mid:]
        # 拼接：上方是左半部分，下方是右半部分
        result = cv2.vconcat([left, right])
    elif mode == "height":
        print(img_path)
        mid = h // 2
        top = img[:mid, :]
        bottom = img[mid:, :]
        # 拼接：左边是上半部分，右边是下半部分
        result = cv2.hconcat([top, bottom])
    else:
        raise ValueError(f"未知处理模式: {mode}")

    return result


def process_folder(folder, mode):
    """处理单个符合条件的文件夹"""
    suffix = "_whalf_cut" if mode == "width" else "_hhalf_cut"
    output_root = folder + suffix

    for root, _, files in os.walk(folder):
        rel_path = os.path.relpath(root, folder)
        out_dir = os.path.join(output_root, rel_path)
        os.makedirs(out_dir, exist_ok=True)

        processed = 0
        for file in files:
            if os.path.splitext(file)[1].lower() in IMG_EXTS:
                in_path = os.path.join(root, file)
                in_path = os.path.normpath(in_path)
                out_path = os.path.join(out_dir, file)
                out_path = os.path.normpath(out_path)

                result = process_image(in_path, mode)
                if result is not None:
                    imwrite_unicode(out_path, result)
                    processed += 1
                    print(f"[OK] {in_path} -> {out_path}")

        print(f"[完成] {root} -> 处理 {processed} 张图片")


def main():
    for base_path in INPUT_PATHS:
        for root, dirs, _ in os.walk(base_path):
            for d in dirs:
                if re.match(FOLDER_PATTERN, d):
                    folder_path = os.path.join(root, d)
                    folder_path = os.path.normpath(folder_path)
                    print(f"[处理目录] {folder_path}")
                    process_folder(folder_path, PROCESS_MODE)


if __name__ == "__main__":
    main()
