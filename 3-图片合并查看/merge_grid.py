#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将按 x-y 命名（x 为行，y 为列，如 1-1.jpg）的图片拼接为一张大图；
或按多个带时间前缀的目录，读取其中的 BoxPR_curve.png 与 MaskPR_curve.png，
按时间从早到晚排列成两行（上：Box，下：Mask）的大图，并在每列上方标注时间。

用法示例：
    # 模式一：x-y 网格合并（与旧功能一致）
    python merge_grid.py --dir "/path/to/images" --output RESULT.jpg

    # 模式二：多目录时间序列合并（每目录含 BoxPR_curve.png、MaskPR_curve.png）
    python merge_grid.py --dirs \
        "D:/.../2025-04-09-04-11_SIM_A/..." \
        "D:/.../2025-04-10-12-30_SIM_B/..." \
        --output RESULT.png --padding 10 --label_height 32

依赖：
    pip install pillow
"""

import argparse
import os
import re
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# 匹配文件名中的行列编号，如 1-2.jpg / 03-12.PNG / 10-1.jpeg
FILENAME_PATTERN = re.compile(r"^(?P<row>\d+)-(?P<col>\d+)\.(?P<ext>png|jpg|jpeg|bmp|webp)$", re.IGNORECASE)

# 匹配目录名中的时间前缀：YYYY-MM-DD-HH-MM_*
TIMESTAMP_PREFIX_PATTERN = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2}-\d{2}-\d{2})")

BOX_NAME = "BoxPR_curve.png"
MASK_NAME = "MaskPR_curve.png"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="图片网格合并工具：x-y 网格或多目录时间序列合并")
    parser.add_argument("--dir", dest="input_dir", default=None, help="x-y 命名图片所在目录（模式一）")
    parser.add_argument("--dirs", nargs='*', dest="input_dirs", default=None, help="按时间排序的多个目录路径（模式二）")
    parser.add_argument("--output", dest="output", default="RESULT.jpg", help="输出文件名（默认 RESULT.jpg）")
    parser.add_argument("--padding", type=int, default=0, help="网格内边距像素（默认 0）")
    parser.add_argument("--bg", dest="bg", default="#FFFFFF", help="背景色，RGB 十六进制，如 #FFFFFF（默认白色）")
    parser.add_argument("--label_height", type=int, default=32, help="时间标签区域高度（模式二，默认 32）")
    parser.add_argument("--font", dest="font_path", default=None, help="可选，自定义字体路径（用于标签绘制）")
    parser.add_argument("--font_size", type=int, default=16, help="标签字体大小（默认 16）")
    return parser.parse_args()


# ==================== 工具函数 ====================

def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
    """兼容不同 Pillow 版本的文本尺寸测量。
    优先使用 draw.textbbox，其次 font.getbbox，再次 font.getsize，最后回退估算。"""
    try:
        # Pillow >= 8: textbbox 可用
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox is not None:
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        pass
    try:
        # 字体对象的 getbbox
        bbox = font.getbbox(text)
        if bbox is not None:
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        pass
    try:
        # 老接口 getsize
        return font.getsize(text)
    except Exception:
        pass
    # 最后兜底：粗略估计宽度=字符数*字体大小*0.6，高度=字体大小
    return max(1, int(len(text) * font.size * 0.6)), max(1, int(font.size))


# ==================== 模式一：x-y 网格 ====================

def load_images(input_dir: str) -> Dict[Tuple[int, int], Image.Image]:
    """加载目录下按 x-y 命名的图片，返回以 (row, col) 为键的图像字典。"""
    images: Dict[Tuple[int, int], Image.Image] = {}
    for name in os.listdir(input_dir):
        match = FILENAME_PATTERN.match(name)
        if not match:
            continue
        row = int(match.group("row"))
        col = int(match.group("col"))
        path = os.path.join(input_dir, name)
        try:
            img = Image.open(path).convert("RGB")
            images[(row, col)] = img
        except Exception as exc:
            print(f"跳过无法读取的文件: {name}，错误: {exc}")
    return images


def compute_grid_shape(keys: List[Tuple[int, int]]) -> Tuple[int, int]:
    """根据 (row, col) 键集合推断网格行列数。"""
    if not keys:
        return 0, 0
    max_row = max(r for r, _ in keys)
    max_col = max(c for _, c in keys)
    return max_row, max_col


def determine_cell_size(images: Dict[Tuple[int, int], Image.Image]) -> Tuple[int, int]:
    """
    统一单元格尺寸：取已加载图片的最大宽、高，避免放大导致失真。
    后续将保持原图等比缩放置于该单元格，空白用背景色填充。
    """
    if not images:
        return 0, 0
    max_w = 0
    max_h = 0
    for img in images.values():
        w, h = img.size
        if w > max_w:
            max_w = w
        if h > max_h:
            max_h = h
    return max_w, max_h


def resize_to_fit(img: Image.Image, cell_size: Tuple[int, int]) -> Image.Image:
    """将图片等比缩放以适配 cell_size，返回尺寸不超过 cell 的图像副本。"""
    cell_w, cell_h = cell_size
    if cell_w == 0 or cell_h == 0:
        return img
    w, h = img.size
    scale = min(cell_w / w, cell_h / h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    return img.resize((new_w, new_h), Image.LANCZOS)


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    s = hex_color.strip().lstrip('#')
    if len(s) == 3:
        s = ''.join([ch * 2 for ch in s])
    if len(s) != 6:
        raise ValueError(f"非法颜色值: {hex_color}")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return (r, g, b)


def compose_grid(images: Dict[Tuple[int, int], Image.Image], rows: int, cols: int, cell_size: Tuple[int, int], padding: int, bg_rgb: Tuple[int, int, int]) -> Image.Image:
    """将图像按网格拼接为大图。缺失位置使用纯背景色填充。"""
    cell_w, cell_h = cell_size
    if rows <= 0 or cols <= 0 or cell_w <= 0 or cell_h <= 0:
        raise ValueError("无有效图片或网格尺寸不可为 0")

    total_w = cols * cell_w + (cols + 1) * padding
    total_h = rows * cell_h + (rows + 1) * padding

    canvas = Image.new("RGB", (total_w, total_h), color=bg_rgb)

    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            x0 = padding + (c - 1) * (cell_w + padding)
            y0 = padding + (r - 1) * (cell_h + padding)

            base = Image.new("RGB", (cell_w, cell_h), color=bg_rgb)
            img = images.get((r, c))
            if img is not None:
                fitted = resize_to_fit(img, (cell_w, cell_h))
                fw, fh = fitted.size
                paste_x = x0 + (cell_w - fw) // 2
                paste_y = y0 + (cell_h - fh) // 2
                canvas.paste(fitted, (paste_x, paste_y))
            else:
                canvas.paste(base, (x0, y0))
    return canvas


# ==================== 模式二：多目录时间序列（Box/Mask） ====================

def parse_ts_from_dirname(dirname: str) -> Optional[datetime]:
    """从目录名中解析时间戳（YYYY-MM-DD-HH-MM 前缀）。"""
    m = TIMESTAMP_PREFIX_PATTERN.match(dirname)
    if not m:
        return None
    ts_text = m.group("ts")
    try:
        return datetime.strptime(ts_text, "%Y-%m-%d-%H-%M")
    except Exception:
        return None


def load_box_mask_images(dir_path: str) -> Tuple[Optional[Image.Image], Optional[Image.Image]]:
    """尝试加载指定目录内的 BoxPR_curve.png 与 MaskPR_curve.png。"""
    box_path = os.path.join(dir_path, BOX_NAME)
    mask_path = os.path.join(dir_path, MASK_NAME)
    box_img = None
    mask_img = None
    if os.path.isfile(box_path):
        try:
            box_img = Image.open(box_path).convert("RGB")
        except Exception as exc:
            print(f"警告：无法读取 {box_path}: {exc}")
    else:
        print(f"警告：未找到 {box_path}")

    if os.path.isfile(mask_path):
        try:
            mask_img = Image.open(mask_path).convert("RGB")
        except Exception as exc:
            print(f"警告：无法读取 {mask_path}: {exc}")
    else:
        print(f"警告：未找到 {mask_path}")

    return box_img, mask_img


def determine_cell_size_from_pairs(pairs: List[Tuple[Optional[Image.Image], Optional[Image.Image]]]) -> Tuple[int, int]:
    """根据一组 (box, mask) 图像对确定统一 cell 尺寸（取最大宽高）。"""
    max_w = 0
    max_h = 0
    for box_img, mask_img in pairs:
        for img in (box_img, mask_img):
            if img is None:
                continue
            w, h = img.size
            if w > max_w:
                max_w = w
            if h > max_h:
                max_h = h
    return max_w, max_h


def compose_time_series_grid(dir_paths: List[str], padding: int, bg_rgb: Tuple[int, int, int], label_height: int, font_path: Optional[str], font_size: int) -> Image.Image:
    """
    按时间从早到晚（列方向）合并多个目录的 Box/Mask 曲线图：
    - 行数固定为 2（第一行 Box，第二行 Mask）
    - 在每列上方单独的标签区绘制该列对应目录的时间戳文本
    """
    # 收集有效目录与其时间
    items: List[Tuple[datetime, str]] = []
    for p in dir_paths:
        if not os.path.isdir(p):
            print(f"跳过非目录路径：{p}")
            continue
        ts = parse_ts_from_dirname(os.path.basename(os.path.normpath(p)))
        if ts is None:
            print(f"跳过无时间前缀目录：{p}")
            continue
        items.append((ts, p))

    if not items:
        raise ValueError("未提供有效的时间前缀目录")

    # 时间升序排序
    items.sort(key=lambda x: x[0])

    # 加载每个目录的两张图片
    pairs: List[Tuple[Optional[Image.Image], Optional[Image.Image]]] = []
    labels: List[str] = []
    for ts, p in items:
        box_img, mask_img = load_box_mask_images(p)
        pairs.append((box_img, mask_img))
        labels.append(ts.strftime("%Y-%m-%d %H:%M"))

    # 统一 cell 尺寸
    cell_w, cell_h = determine_cell_size_from_pairs(pairs)
    if cell_w <= 0 or cell_h <= 0:
        raise ValueError("无法确定单元格尺寸，请检查图像是否存在")

    cols = len(pairs)
    rows = 2

    total_w = cols * cell_w + (cols + 1) * padding
    total_h = label_height + rows * cell_h + (rows + 1) * padding

    canvas = Image.new("RGB", (total_w, total_h), color=bg_rgb)
    draw = ImageDraw.Draw(canvas)

    # 字体
    font: ImageFont.ImageFont
    if font_path and os.path.isfile(font_path):
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            font = ImageFont.load_default()
    else:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

    # 绘制每列
    for idx, ((box_img, mask_img), label) in enumerate(zip(pairs, labels), start=0):
        # 列左上角起点（含 padding）
        col_x0 = padding + idx * (cell_w + padding)

        # 标签区域（单独一行高度）
        label_area_x0 = col_x0
        label_area_y0 = padding
        label_area_x1 = col_x0 + cell_w
        label_area_y1 = padding + label_height

        # 文本居中绘制（兼容不同 Pillow 版本）
        text_w, text_h = measure_text(draw, label, font)
        text_x = label_area_x0 + (cell_w - text_w) // 2
        text_y = label_area_y0 + (label_height - text_h) // 2
        draw.text((text_x, text_y), label, fill=(0, 0, 0), font=font)

        # 第一行（Box）图像区域起点
        row1_y0 = label_area_y1 + padding  # 标签下方再加一层 padding
        if box_img is not None:
            fitted = resize_to_fit(box_img, (cell_w, cell_h))
            fw, fh = fitted.size
            paste_x = col_x0 + (cell_w - fw) // 2
            paste_y = row1_y0 + (cell_h - fh) // 2
            canvas.paste(fitted, (paste_x, paste_y))
        # 第二行（Mask）
        row2_y0 = row1_y0 + cell_h + padding
        if mask_img is not None:
            fitted = resize_to_fit(mask_img, (cell_w, cell_h))
            fw, fh = fitted.size
            paste_x = col_x0 + (cell_w - fw) // 2
            paste_y = row2_y0 + (cell_h - fh) // 2
            canvas.paste(fitted, (paste_x, paste_y))

    return canvas


def main() -> None:
    args = parse_args()

    # 解析通用参数
    output_path = args.output if os.path.isabs(args.output) else os.path.join(os.getcwd(), args.output)
    padding = max(0, int(args.padding))
    try:
        bg_rgb = hex_to_rgb(args.bg)
    except Exception as exc:
        raise SystemExit(f"背景色解析失败: {exc}")

    # 模式判断：优先使用 --dirs（模式二），否则回退到 --dir（模式一）
    if args.input_dirs and len(args.input_dirs) > 0:
        try:
            grid = compose_time_series_grid(
                dir_paths=args.input_dirs,
                padding=padding,
                bg_rgb=bg_rgb,
                label_height=max(0, int(args.label_height)),
                font_path=args.font_path,
                font_size=int(args.font_size),
            )
        except Exception as exc:
            raise SystemExit(f"时间序列合并失败: {exc}")
    else:
        # 模式一：x-y 网格
        input_dir = args.input_dir or "."
        if not os.path.isdir(input_dir):
            raise SystemExit(f"目录不存在: {input_dir}")
        images = load_images(input_dir)
        if not images:
            raise SystemExit("未在目录中找到符合 x-y 命名的图片文件")
        rows, cols = compute_grid_shape(list(images.keys()))
        cell_size = determine_cell_size(images)
        try:
            grid = compose_grid(images, rows, cols, cell_size, padding, bg_rgb)
        except Exception as exc:
            raise SystemExit(f"网格合并失败: {exc}")

    # 输出文件夹若不存在则尝试创建
    out_dir = os.path.dirname(output_path) or "."
    os.makedirs(out_dir, exist_ok=True)

    try:
        grid.save(output_path)
        print(f"已保存: {output_path}")
    except Exception as exc:
        raise SystemExit(f"保存失败: {exc}")


if __name__ == "__main__":
    main() 