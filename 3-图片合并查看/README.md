# 图片网格合并工具（x-y 命名 + 多目录时间序列）

支持两种模式：
- 模式一：按 `x-y`（行-列）命名的图片自动网格合并
- 模式二：输入多个带时间前缀的目录（如 `2025-04-09-04-11_xxx`），读取各目录下的 `BoxPR_curve.png` 和 `MaskPR_curve.png`，按时间从早到晚排成两行（上 `Box` 下 `Mask`），并在每列上方绘制时间标签

## 安装依赖

- 需要 Python 3.8+
- 安装 Pillow：

```bash
pip install pillow
```

## 模式一：x-y 网格合并（原功能）

在图片所在目录执行，或用 `--dir` 指定目录：

```bash
# 在图片目录内执行
python merge_grid.py --output RESULT.jpg

# 在任意目录执行，指定图片目录
python 3-图片合并查看/merge_grid.py --dir "D:/path/to/images" --output RESULT.jpg
```

可选参数：
- `--padding`: 单元格与边缘的像素间距（默认 0）
- `--bg`: 背景颜色，十六进制 RGB，如 `#FFFFFF`（默认白色）

命名规则：`x-y.ext`（x 行，y 列，起始 1），支持 `png/jpg/jpeg/bmp/webp`。

## 模式二：多目录时间序列合并（Box/Mask + 时间标签）

目录命名要求：带时间前缀 `YYYY-MM-DD-HH-MM_...`，例如：
- `2025-04-09-04-11_SIM_Airtag_G_yolov5s6-seg_hyp.scratch-low`
- `2025-04-10-12-30_SIM_B_...`

每个目录下应包含：
- `BoxPR_curve.png`
- `MaskPR_curve.png`

示例：

```bash
python 3-图片合并查看/merge_grid.py \
  --dirs \
  "D:/exp/2025-04-09-04-11_SIM_Airtag_G_yolov5s6-seg_hyp.scratch-low" \
  "D:/exp/2025-04-11-09-20_SIM_B_model" \
  "D:/exp/2025-04-12-18-40_SIM_C_model" \
  --output RESULT.png --padding 10 --bg #FFFFFF --label_height 32 --font_size 16
```

说明：
- 将按时间从早到晚排序，最早的在第一列，最迟的在最后一列
- 固定两行：第一行拼接 `BoxPR_curve.png`，第二行拼接 `MaskPR_curve.png`
- 每列上方绘制该目录解析出的时间（格式：`YYYY-MM-DD HH:MM`）
- 若某目录缺少某一张图，会留白（使用背景色填充）

可选参数（在模式二中同样生效）：
- `--label_height`：顶部标签区高度（默认 32）
- `--font`：标签字体文件路径（可选，不提供则使用默认字体）
- `--font_size`：标签字体大小（默认 16）

## 尺寸与缩放规则（两种模式通用）

- 自动选取需要合并图片中的最大宽、高作为单元格大小
- 每张图片将等比缩放以适配单元格，并在单元格中居中显示
- 未提供的单元格位置用背景色填充

## 输出

- 默认输出到当前工作目录下的 `RESULT.jpg`（可自定义文件名或使用绝对路径）
- 如需保留透明背景，请输出 PNG（例如设置 `--output RESULT.png`）

## 常见问题

- 无法识别时间：请确保目录名以 `YYYY-MM-DD-HH-MM_` 开头
- 缺少曲线图：检查目录下是否存在 `BoxPR_curve.png` 和 `MaskPR_curve.png`
- 字体不美观：可通过 `--font` 指定本地 `.ttf` 字体文件并设置 `--font_size` 