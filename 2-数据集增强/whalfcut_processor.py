import os
import argparse
from pathlib import Path
from typing import List, Tuple
from PIL import Image


def parse_bg_color(color_str: str) -> Tuple[int, int, int]:
    """解析背景色参数"""
    named_colors = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
    }
    if not color_str:
        return (0, 0, 0)
    
    lower = color_str.lower()
    if lower in named_colors:
        return named_colors[lower]
    
    if lower.startswith('#') and len(lower) == 7:
        try:
            r = int(lower[1:3], 16)
            g = int(lower[3:5], 16)
            b = int(lower[5:7], 16)
            return (r, g, b)
        except ValueError:
            pass
    
    raise ValueError(f"不支持的背景色格式: {color_str}")


def is_image_file(file_path: Path, extensions: List[str]) -> bool:
    """判断是否为支持的图片文件"""
    return file_path.is_file() and file_path.suffix.lower().lstrip('.') in [ext.lower().lstrip('.') for ext in extensions]


def process_image_half_cut(image_path: Path, output_path: Path, bg_color: Tuple[int, int, int], align: str) -> bool:
    """处理单张图片：按宽度一半截断，右半部分拼接到左半部分下方"""
    try:
        with Image.open(str(image_path)) as img:
            # 转换为RGB模式
            img = img.convert('RGB')
            width, height = img.size
            
            if width < 2:
                print(f"[警告] 图片宽度过小，跳过: {image_path}")
                return False
            
            # 计算中点
            mid_point = width // 2
            
            # 裁剪左半部分和右半部分
            left_half = img.crop((0, 0, mid_point, height))
            right_half = img.crop((mid_point, 0, width, height))
            
            # 创建画布：宽度取两半中较大的，高度为两半之和
            canvas_width = max(left_half.width, right_half.width)
            canvas_height = left_half.height + right_half.height
            canvas = Image.new('RGB', (canvas_width, canvas_height), bg_color)
            
            # 计算粘贴位置
            def get_x_offset(part_width: int) -> int:
                if align == 'center':
                    return (canvas_width - part_width) // 2
                return 0
            
            # 粘贴左半部分到上方
            left_x = get_x_offset(left_half.width)
            canvas.paste(left_half, (left_x, 0))
            
            # 粘贴右半部分到下方
            right_x = get_x_offset(right_half.width)
            canvas.paste(right_half, (right_x, left_half.height))
            
            # 保存处理后的图片
            output_path.parent.mkdir(parents=True, exist_ok=True)
            canvas.save(str(output_path))
            
            print(f"[成功] {image_path.name} -> {output_path}")
            return True
            
    except Exception as e:
        print(f"[错误] 处理图片失败 {image_path}: {str(e)}")
        return False


def process_directory(input_dir: Path, output_base_dir: Path, extensions: List[str], 
                     bg_color: Tuple[int, int, int], align: str) -> int:
    """处理目录下的所有图片"""
    processed_count = 0
    
    # 遍历所有子目录
    for item in input_dir.iterdir():
        if item.is_dir():
            # 创建对应的输出目录，名称加上_whalfcut标识
            output_dir_name = f"{item.name}_whalfcut"
            output_dir = output_base_dir / output_dir_name
            
            print(f"\n处理目录: {item.name} -> {output_dir_name}")
            
            # 处理该目录下的所有图片
            for file_path in item.iterdir():
                if is_image_file(file_path, extensions):
                    # 构建输出文件路径
                    output_file = output_dir / file_path.name
                    
                    # 处理图片
                    if process_image_half_cut(file_path, output_file, bg_color, align):
                        processed_count += 1
    
    return processed_count


def main():
    parser = argparse.ArgumentParser(
        description='批量处理图片：按宽度一半截断，右半部分拼接到左半部分下方'
    )
    parser.add_argument('--input_path', default='C:\\Users\\Administrator\\Desktop\\领益B25\\新增缺陷取图\\新增缺陷取图\\A-查看数据G面\\内侧划伤')
    parser.add_argument('--output-dir', help='输出基础目录（可选，默认与输入路径相同）')
    parser.add_argument('--exts', default='jpg,jpeg,png,bmp,webp', 
                       help='支持的图片扩展名，逗号分隔，默认: jpg,jpeg,png,bmp,webp')
    parser.add_argument('--bg', default='#000000', 
                       help='背景色，支持#RRGGBB或white/black/gray，默认#000000')
    parser.add_argument('--align', choices=['left', 'center'], default='left',
                       help='左右对齐方式（当左右宽度不等时），默认left')
    
    args = parser.parse_args()
    
    # 解析参数
    input_path = Path(args.input_path)
    output_base_dir = Path(args.output_dir) if args.output_dir else input_path
    extensions = [ext.strip() for ext in args.exts.split(',') if ext.strip()]
    bg_color = parse_bg_color(args.bg)
    
    # 检查输入路径
    if not input_path.exists():
        print(f"错误：输入路径不存在: {input_path}")
        return
    
    if not input_path.is_dir():
        print(f"错误：输入路径不是目录: {input_path}")
        return
    
    print(f"开始处理...")
    print(f"输入路径: {input_path}")
    print(f"输出基础目录: {output_base_dir}")
    print(f"支持的扩展名: {', '.join(extensions)}")
    print(f"背景色: {args.bg}")
    print(f"对齐方式: {args.align}")
    
    # 处理所有子目录
    total_processed = process_directory(input_path, output_base_dir, extensions, bg_color, args.align)
    
    print(f"\n处理完成！共处理 {total_processed} 张图片")
    print(f"输出目录已创建在: {output_base_dir}")


if __name__ == '__main__':
    main() 