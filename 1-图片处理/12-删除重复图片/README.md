# 删除重复图片脚本

这个脚本用于删除带有(2)、(3)等后缀的重复图片文件。

## 功能特点

- 支持多个目录路径同时处理
- 自动识别重复图片（原图没有(2)，重复图片有(2)等后缀）
- 支持试运行模式，可以先预览要删除的文件
- 详细的日志记录
- 支持多种图片格式：jpg, jpeg, png, bmp, gif, tiff, tif, webp

## 使用方法

### 基本用法

```bash
# 处理单个目录
python remove_duplicate_images.py "C:\path\to\images"

# 处理多个目录
python remove_duplicate_images.py "C:\path1" "C:\path2" "C:\path3"
```

### 试运行模式

在正式删除前，建议先使用试运行模式查看将要删除的文件：

```bash
python remove_duplicate_images.py --dry-run "C:\path\to\images"
```

### 其他选项

```bash
# 设置日志级别
python remove_duplicate_images.py --log-level DEBUG "C:\path\to\images"

# 查看帮助
python remove_duplicate_images.py --help
```

## 工作原理

1. 脚本会递归扫描指定目录下的所有图片文件
2. 使用正则表达式识别文件名模式：`文件名(数字).扩展名`
3. 将相同基础名称的文件分组
4. 保留原图（没有(2)等后缀），删除重复文件（有(2)、(3)等后缀）

## 示例

假设有以下文件：
- `G1_20250830191306412_4.jpg` (原图)
- `G1_20250830191306412_4(2).jpg` (重复文件)
- `G1_20250830191306412_4(3).jpg` (重复文件)

脚本会保留 `G1_20250830191306412_4.jpg`，删除其他两个重复文件。

## 安全提示

- 建议先使用 `--dry-run` 参数预览要删除的文件
- 脚本会生成详细的日志文件 `duplicate_removal.log`
- 删除操作不可逆，请谨慎使用
