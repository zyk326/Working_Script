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
SOURCE_PATH = r"C:\Users\Administrator\Desktop\BBB\BBB"  # 修改为你的源路径

# 目标路径：结果将保存到该路径下的result文件夹
TARGET_PATH = r"C:\Users\Administrator\Desktop\BBB\BBB-allliuwen"    # 修改为你的目标路径

# 单标签（向后兼容）。当 TARGET_LABELS 非空时将被忽略
TARGET_LABEL = "压伤"   # 可以修改为其他标签

# 多标签支持：填写多个需要匹配的标签；若留空将回退到 TARGET_LABEL
TARGET_LABELS = [
	"法兰流纹",
]

# 是否启用试运行模式（True=只预览不复制/剪切，False=实际执行）
DRY_RUN = False

# 是否使用剪切替代复制（True=剪切，即移动文件；False=复制）
MOVE_INSTEAD_OF_COPY = False

# 是否保留与源路径一致的相对目录结构（True=保留；False=不保留，全部直接放在 result 下）
PRESERVE_RELATIVE_STRUCTURE = False

# 新增：是否将指定标签作为“排除”规则（True=出现任一指定标签则跳过不复制；False=出现任一指定标签则复制）
EXCLUDE_ON_LABELS = False

# ==================== 配置区域结束 ====================


def _effective_labels() -> list:
	labels = [l for l in TARGET_LABELS if str(l).strip()] if TARGET_LABELS else [TARGET_LABEL]
	return labels


def _matches_any_label(shape_label: str) -> bool:
	"""判断给定 shape 的 label 是否命中目标标签（支持多标签，子串匹配）。"""
	try:
		label_text = str(shape_label)
	except Exception:
		return False
	for t in _effective_labels():
		if not str(t):
			continue
		if str(t) in label_text:
			return True
	return False


def find_and_copy_files_with_label(source_path: str, target_label: str, target_path: str, dry_run: bool = False) -> int:
	"""
	在指定路径下递归查找包含目标标签的JSON文件，找到后根据规则复制/剪切
	（可选：保持与源路径一致的相对目录结构）
	
	Args:
		source_path: 源路径
		target_label: 目标标签名称（当 TARGET_LABELS 非空时忽略此参数）
		target_path: 目标路径
		dry_run: 是否为试运行模式
		
	Returns:
		成功复制/剪切的文件对数
	"""
	copied_count = 0
	
	print(f"正在扫描路径: {source_path}")
	print("=" * 60)
	
	# 创建result文件夹
	result_root = os.path.join(target_path, "result")
	if not dry_run:
		os.makedirs(result_root, exist_ok=True)
		print(f"创建目标根文件夹: {result_root}")
	else:
		print(f"试运行模式：将创建目标根文件夹: {result_root}")
	
	mode_str = "剪切(移动)" if MOVE_INSTEAD_OF_COPY else "复制"
	struct_str = "保留相对结构" if PRESERVE_RELATIVE_STRUCTURE else "不保留相对结构"
	labels_desc = _effective_labels()
	rule_str = "排除(出现即跳过)" if EXCLUDE_ON_LABELS else "包含(出现即复制)"
	print(f"目标标签: {labels_desc}  匹配规则: {rule_str}")
	print(f"开始查找并{mode_str}文件（{struct_str}）...")
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
					# 解析 shapes
					shapes = data.get('shapes', [])
					if not isinstance(shapes, list):
						continue
					# 计算是否命中任一标签
					matched = False
					for shape in shapes:
						if not isinstance(shape, dict):
							continue
						label_value = shape.get('label')
						if label_value is None:
							continue
						if _matches_any_label(label_value):
							matched = True
							break
					# 排除模式：命中则跳过；包含模式：命中才复制
					if EXCLUDE_ON_LABELS:
						if matched:
							# 命中排除标签，跳过该对
							continue
					else:
						if not matched:
							# 未命中包含标签，跳过
							continue
					# 检查对应图片
					image_name = data.get('imagePath', '')
					if image_name:
						image_path = os.path.join(root, image_name)
						if os.path.exists(image_path):
							# 目标子目录
							if PRESERVE_RELATIVE_STRUCTURE:
								rel_dir = os.path.relpath(root, source_path)
								target_dir = os.path.join(result_root, rel_dir)
							else:
								target_dir = result_root
							if not dry_run:
								os.makedirs(target_dir, exist_ok=True)
								print(f"确保目标子目录: {target_dir}")
							else:
								print(f"[DRY-RUN] 将创建目标子目录: {target_dir}")
							# 执行复制/剪切
							copied = copy_or_move_single_file_pair(json_path, image_path, target_dir, dry_run)
							if copied:
								copied_count += 1
								print(f"✓ 已{mode_str}第 {copied_count} 对文件 -> {target_dir}")
							print()
						else:
							print(f"警告：JSON文件存在但对应图片不存在: {image_path}")
				except json.JSONDecodeError as e:
					print(f"警告：无法解析JSON文件 {json_path}: {e}")
				except Exception as e:
					print(f"警告：处理文件 {json_path} 时出错: {e}")
	
	return copied_count


def copy_or_move_single_file_pair(json_path: str, image_path: str, result_dir: str, dry_run: bool = False) -> bool:
	"""
	复制或剪切单个文件对（JSON + 图片）到指定的结果子目录
	
	Args:
		json_path: JSON文件路径
		image_path: 图片文件路径
		result_dir: 目标子目录（可能是 result 根，或附加相对结构）
		dry_run: 是否为试运行模式
		
	Returns:
		是否处理成功
	"""
	# 获取文件名
	json_name = os.path.basename(json_path)
	image_name = os.path.basename(image_path)
	
	# 目标路径
	target_json = os.path.join(result_dir, json_name)
	target_image = os.path.join(result_dir, image_name)
	
	if dry_run:
		mode_str = "剪切(移动)" if MOVE_INSTEAD_OF_COPY else "复制"
		print(f"[DRY-RUN] 将{mode_str} {json_name} 和 {image_name} -> {result_dir}")
		return True
	
	try:
		# 确保目录存在
		os.makedirs(result_dir, exist_ok=True)
		if MOVE_INSTEAD_OF_COPY:
			# 剪切（移动）JSON与图片
			shutil.move(json_path, target_json)
			print(f"✓ 剪切JSON: {json_name}")
			shutil.move(image_path, target_image)
			print(f"✓ 剪切图片: {image_name}")
		else:
			# 复制JSON与图片
			shutil.copy2(json_path, target_json)
			print(f"✓ 复制JSON: {json_name}")
			shutil.copy2(image_path, target_image)
			print(f"✓ 复制图片: {image_name}")
		return True
		
	except Exception as e:
		mode_str = "剪切" if MOVE_INSTEAD_OF_COPY else "复制"
		print(f"✗ {mode_str}失败 {json_name}/{image_name}: {e}")
		return False


def main():
	"""主函数"""
	print("钢网毛刺图片筛选工具 v2.0")
	print("=" * 50)
	print(f"源路径: {SOURCE_PATH}")
	print(f"目标路径: {TARGET_PATH}")
	print(f"目标标签: {_effective_labels()}")
	print(f"匹配规则: {'排除(出现即跳过)' if EXCLUDE_ON_LABELS else '包含(出现即复制)'}")
	print(f"试运行模式: {'是' if DRY_RUN else '否'}")
	print(f"处理模式: {'剪切(移动)' if MOVE_INSTEAD_OF_COPY else '复制'}")
	print(f"目录结构: {'保留相对结构' if PRESERVE_RELATIVE_STRUCTURE else '不保留相对结构'}")
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
	
	# 查找并按规则处理包含目标标签的文件
	copied_count = find_and_copy_files_with_label(SOURCE_PATH, TARGET_LABEL, TARGET_PATH, DRY_RUN)
	
	if copied_count == 0:
		print("未找到需要复制/剪切的文件")
		return
	
	if not DRY_RUN:
		print("=" * 60)
		mode_str = "剪切(移动)" if MOVE_INSTEAD_OF_COPY else "复制"
		print(f"完成！成功{mode_str}了 {copied_count} 对文件")
		print(f"结果保存在: {os.path.join(TARGET_PATH, 'result')} ")
	else:
		print("=" * 60)
		print("试运行完成！")
		print(f"将处理 {copied_count} 对文件到: {os.path.join(TARGET_PATH, 'result')} ")
		print("如需实际执行，请将 DRY_RUN 设置为 False")


if __name__ == "__main__":
	main() 