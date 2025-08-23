# 图片批量处理：宽度一半截断并下拼

本脚本用于批量处理指定路径下所有子文件夹中的图片，将每张图片按宽度的一半截断，然后将右半部分拼接到左半部分的下方。

## 功能特点

- **批量处理**：自动遍历指定路径下的所有子文件夹
- **智能命名**：输出文件夹自动添加 `_whalfcut` 标识
- **保持结构**：输出目录结构与输入完全对应
- **多种格式**：支持 jpg、jpeg、png、bmp、webp 等常见图片格式
- **灵活配置**：可自定义背景色和对齐方式

## 安装依赖

```bash
pip install pillow
```

## 使用方法

### 基本用法

```bash
python whalfcut_processor.py "输入路径"
```

### 完整参数示例

```bash
python whalfcut_processor.py "D:\图片库" --output-dir "D:\处理后图片" --bg white --align center
```

## 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `input_path` | 输入路径（必需） | - | `"D:\图片库"` |
| `--output-dir` | 输出基础目录 | 与输入路径相同 | `--output-dir "D:\输出"` |
| `--exts` | 支持的图片扩展名 | `jpg,jpeg,png,bmp,webp` | `--exts jpg,png` |
| `--bg` | 背景色 | `#000000`（黑色） | `--bg white` 或 `--bg #FFFFFF` |
| `--align` | 左右对齐方式 | `left` | `--align center` |

## 背景色支持

- **命名颜色**：`white`、`black`、`gray`、`grey`
- **十六进制**：`#RRGGBB` 格式，如 `#FF0000`（红色）

## 对齐方式

- **`left`**：左对齐（默认）
- **`center`**：居中对齐

## 处理流程

1. 扫描输入路径下的所有子文件夹
2. 对每个子文件夹：
   - 创建对应的输出文件夹（名称 + `_whalfcut`）
   - 处理该文件夹下的所有图片
3. 对每张图片：
   - 按宽度中点垂直分割
   - 左半部分放在上方
   - 右半部分放在下方
   - 保存到对应的输出文件夹

## 输出示例

**输入结构：**
```
D:\图片库\
├── 风景照\
│   ├── 山水.jpg
│   └── 海景.png
└── 人像\
    ├── 正面.jpg
    └── 侧面.png
```

**输出结构：**
```
D:\图片库\
├── 风景照_whalfcut\
│   ├── 山水.jpg
│   └── 海景.png
└── 人像_whalfcut\
    ├── 正面.jpg
    └── 侧面.png
```

## 注意事项

- 确保输入路径存在且包含子文件夹
- 图片宽度必须大于等于2像素
- 处理大图片时可能需要较长时间
- 输出文件夹会自动创建，无需手动创建
- 支持断点续处理（重新运行会覆盖已存在的文件）

## 错误处理

脚本会显示详细的处理进度和错误信息：
- `[成功]`：图片处理成功
- `[警告]`：图片宽度过小，跳过处理
- `[错误]`：处理过程中出现异常

## 示例命令

```bash
# 基本使用（输出到同目录）
python whalfcut_processor.py （需要手动在代码里更改默认的图片文件夹路径）

# 指定输出目录和白色背景
python whalfcut_processor.py "C:\Users\用户名\Pictures" --output-dir "C:\处理后图片" --bg white

# 只处理jpg和png文件，居中对齐
python whalfcut_processor.py "C:\Users\用户名\Pictures" --exts jpg,png --align center
``` 