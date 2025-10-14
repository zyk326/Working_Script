#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil
from typing import Dict, Iterable, List, Optional, Set, Tuple

# =========================
# 配置区：在此直接修改参数
# =========================
# 多个源根目录：递归查找其中名称为单个大写字母+数字（如 A1/B1）的文件夹
ROOT_DIRS = [
	# r"Y:\\path\\to\\root1",
	# r"Y:\\path\\to\\root2",
    r"Y:\4_训练数据\2025-06-24立讯 吉安  国产手机充电器 Cos AOI\20250904",
]

# 输出根目录：将保持相对每个源根目录的结构进行保存
OUT_ROOT = r"Y:\4_训练数据\2025-06-24立讯 吉安  国产手机充电器 Cos AOI\20250904-pair"

# 处理模式：是否剪切替代复制（True=剪切/移动；False=复制）
MOVE_INSTEAD_OF_COPY = False

# 处理对象："pair" 表示图片对（图片+同名json）；"single" 表示单个图片（无对应json）
PROCESS_TARGET = "pair"  # 可选值："pair" 或 "single"

# 图片扩展名（用于识别图片文件）
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

# 是否试运行（True 打印计划，不实际执行）
DRY_RUN = False

# 是否递归遍历（一般为 True）
RECURSIVE = True

# A1/B1 等目录名匹配规则：单个大写字母 + 单个数字
FOLDER_NAME_PATTERN = re.compile(r"^[A-Z][0-9]$")


# ========================= 实现 =========================

def ensure_dir(path: str) -> None:
	if not os.path.isdir(path):
		os.makedirs(path, exist_ok=True)


def iter_prefixed_dirs(root: str, recursive: bool) -> Iterable[str]:
	root_abs = os.path.abspath(root)
	if recursive:
		for dirpath, dirnames, _ in os.walk(root_abs):
			for d in dirnames:
				if FOLDER_NAME_PATTERN.match(d):
					yield os.path.join(dirpath, d)
	else:
		for d in os.listdir(root_abs):
			full = os.path.join(root_abs, d)
			if os.path.isdir(full) and FOLDER_NAME_PATTERN.match(d):
				yield full


def relative_dst_dir(src_root: str, matched_dir: str, out_root: str) -> str:
	rel = os.path.relpath(matched_dir, os.path.abspath(src_root))
	return os.path.join(os.path.abspath(out_root), rel)


def copy_or_move_file(src: str, dst: str, move: bool, dry_run: bool) -> None:
	ensure_dir(os.path.dirname(dst))
	if dry_run:
		op = "MOVE" if move else "COPY"
		print(f"[DRY-RUN] {op}: {src} -> {dst}")
		return
	if move:
		# 若目标存在同名文件，先删除以保证覆盖行为一致
		if os.path.exists(dst):
			os.remove(dst)
		shutil.move(src, dst)
	else:
		# 复制并覆盖（copy2 + 替换）
		if os.path.exists(dst):
			os.remove(dst)
		shutil.copy2(src, dst)


def process_pair_dir(src_dir: str, out_dir: str, image_exts: Set[str], move: bool, dry_run: bool) -> Tuple[int, int]:
	"""
	处理图片对：图片 + 同名 json；copy/move 到 out_dir。
	返回 (pairs_processed, singles_skipped)
	"""
	pairs = 0
	skipped = 0
	for fn in os.listdir(src_dir):
		base, ext = os.path.splitext(fn)
		if ext.lower() in image_exts:
			img_path = os.path.join(src_dir, fn)
			json_path = os.path.join(src_dir, base + ".json")
			if os.path.isfile(json_path):
				# 图片对
				copy_or_move_file(img_path, os.path.join(out_dir, os.path.basename(img_path)), move, dry_run)
				copy_or_move_file(json_path, os.path.join(out_dir, os.path.basename(json_path)), move, dry_run)
				pairs += 1
			else:
				skipped += 1
	return pairs, skipped


def process_single_dir(src_dir: str, out_dir: str, image_exts: Set[str], move: bool, dry_run: bool) -> Tuple[int, int]:
	"""
	处理单个图片：仅复制/剪切没有同名 json 的图片。
	返回 (singles_processed, pairs_skipped)
	"""
	singles = 0
	skipped = 0
	for fn in os.listdir(src_dir):
		base, ext = os.path.splitext(fn)
		if ext.lower() in image_exts:
			img_path = os.path.join(src_dir, fn)
			json_path = os.path.join(src_dir, base + ".json")
			if not os.path.isfile(json_path):
				# 单个图片
				copy_or_move_file(img_path, os.path.join(out_dir, os.path.basename(img_path)), move, dry_run)
				singles += 1
			else:
				skipped += 1
	return singles, skipped


def main() -> None:
	print("筛选图片对或单项 工具")
	print("=" * 60)
	print(f"根路径数量: {len(ROOT_DIRS)}")
	print(f"输出路径: {OUT_ROOT}")
	print(f"处理对象: {PROCESS_TARGET}  (pair=图片+json; single=仅图片)")
	print(f"处理方式: {'剪切' if MOVE_INSTEAD_OF_COPY else '复制'}")
	print(f"递归: {RECURSIVE}  试运行: {DRY_RUN}")
	
	if not ROOT_DIRS:
		print("请在配置中设置 ROOT_DIRS")
		return
	
	ensure_dir(OUT_ROOT)
	
	total_dirs = 0
	processed_files = 0
	skipped_files = 0
	for src_root in ROOT_DIRS:
		src_root_abs = os.path.abspath(src_root)
		if not os.path.isdir(src_root_abs):
			print(f"跳过不存在的根路径: {src_root}")
			continue
		print(f"\n扫描根路径: {src_root_abs}")
		for matched in iter_prefixed_dirs(src_root_abs, RECURSIVE):
			total_dirs += 1
			out_dir = relative_dst_dir(src_root_abs, matched, OUT_ROOT)
			print(f"  处理目录: {matched} -> {out_dir}")
			ensure_dir(out_dir)
			if PROCESS_TARGET == "pair":
				pairs, skipped = process_pair_dir(matched, out_dir, IMAGE_EXTS, MOVE_INSTEAD_OF_COPY, DRY_RUN)
				processed_files += pairs * 2
				skipped_files += skipped
			elif PROCESS_TARGET == "single":
				singles, skipped = process_single_dir(matched, out_dir, IMAGE_EXTS, MOVE_INSTEAD_OF_COPY, DRY_RUN)
				processed_files += singles
				skipped_files += skipped
			else:
				print(f"  未知 PROCESS_TARGET: {PROCESS_TARGET}，应为 'pair' 或 'single'")
				break
	
	print("\n—— 完成 ——")
	print(f"匹配目录数: {total_dirs}")
	print(f"处理文件数: {processed_files}")
	print(f"跳过文件数: {skipped_files}")


if __name__ == "__main__":
	main() 