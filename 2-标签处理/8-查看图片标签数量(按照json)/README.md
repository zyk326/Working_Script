# 查看图片标签数量（代码内配置版）

本工具递归遍历给定根目录，读取同名 JSON（如 `abc.json`）中的 `shapes[*].label`，统计：
- 各缺陷标签出现的总次数（每个标注算一次）
- 包含该缺陷的图片数量（同一图片命中多个相同标签只计 1 次）

无需命令行参数，直接在脚本顶部修改常量即可运行。

## 文件
- `count_defects.py`：统计脚本

## 配置
打开 `count_defects.py` 顶部，修改：
- `ROOT_DIR`：需要统计的根目录
- `IMAGE_EXTS`：用于识别图片文件的后缀列表；设为 `None` 使用默认（`.jpg .jpeg .png .bmp .tif .tiff`）

示例：
```python
ROOT_DIR = r"D:\\data\\root"
IMAGE_EXTS = None  # 或 [".jpg", ".png"]
```

## 运行
```bash
python 8-查看图片标签数量/count_defects.py
```

## 输出示例
```
统计目录: D:\data\root
图片后缀: ['.bmp', '.jpeg', '.jpg', '.png', '.tif', '.tiff']
—— 统计结果 ——
JSON 文件数: 1234
含标注的 JSON 数: 1200
存在同名图片的对数: 1180
各缺陷标注出现次数（label 计次）:
  裂纹: 542
  崩边: 320
包含该缺陷的图片数量（去重每图片）:
  裂纹: 500
  酚边: 300
```

## 说明
- 若某些 JSON 没有同名图片，仍统计其 `label` 出现次数，但不会计入“包含该缺陷的图片数量”。
- 请确保 JSON 编码为 UTF-8，`shapes` 为数组且内含 `label` 字段；支持 `label` 为字符串或列表的情况。 