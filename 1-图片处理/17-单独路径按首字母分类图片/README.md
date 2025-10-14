# 按大写首字母归类并移动图片（含同名 JSON）

将指定目录下所有以相同大写字母开头的图片移动到同路径下以该字母命名的文件夹中；若图片旁存在同名 `*.json`，一并移动到相同目标文件夹。

示例：`A1_3232.jpg`、`A2_2r3242.png` 都会被移动到 `./A/` 目录；若存在 `A1_3232.json`、`A2_2r3242.json`，也会同步移动到 `./A/`。

## 脚本位置
`17-按大写前缀移动图片/move_upper_prefix_images.py`

## 快速开始
1. 打开脚本文件，在顶部“配置区”修改：
   - `BASE_DIR`: 要处理的根目录（例如 `r"D:\\BohrEnv\\ImagesToMove"`）
   - `RECURSIVE`: 是否递归处理子目录（默认 False）
   - `DRY_RUN`: 试运行，先查看将要移动的结果（默认 False，可先设为 True）
   - `AUTO_RENAME_ON_CONFLICT`: 目标已存在同名文件时，是否自动重命名（默认 True）
2. 在 PowerShell 或 CMD 中运行：

```bash
python 17-按大写前缀移动图片/move_upper_prefix_images.py
```

## 处理规则
- 图片扩展名：`jpg, jpeg, png, bmp, gif, tif, tiff, webp`
- 文件名首字符需为大写字母 `A-Z`，按此字母归类到对应文件夹。
- 若存在同名 JSON（如 `A1_3232.jpg` 对应 `A1_3232.json`），会一并移动到相同目标文件夹。
- 当 `RECURSIVE=False`：仅扫描 `BASE_DIR` 第一层文件，目标文件夹建在 `BASE_DIR`。
- 当 `RECURSIVE=True`：递归扫描，目标文件夹建在每个文件的父目录中。
- 同名冲突：
  - `AUTO_RENAME_ON_CONFLICT=True` 时自动追加 `_1`, `_2`, ...
  - 否则保留原名（可能覆盖，建议保持自动重命名）。

## 建议流程
1. 设置 `DRY_RUN=True`，先试运行检查输出。
2. 确认无误后将 `DRY_RUN=False` 进行实际移动。

## 常见问题
- Windows 路径建议用原始字符串 `r"..."` 或双反斜杠 `\\`。
- 确保对目标目录有写权限，文件未被占用。
- UTF-8 编码，支持常见中文文件名。

## 免责声明
移动会改变目录结构，建议先备份或使用试运行确认后再执行。 