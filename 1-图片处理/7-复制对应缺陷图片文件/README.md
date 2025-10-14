# 复制含缺陷图片-JSON对（保留原路径结构）

本工具递归遍历源目录，查找同名的图片与 JSON（如 `abc.jpg` 与 `abc.json`），从 JSON 的 `shapes[*].label` 中读取缺陷名称。命中任一指定缺陷即复制该图片与 JSON，并将其按源目录相对路径保存到输出根目录。每张图片只参与一次复制，受全局上限控制。

## 文件
- `copy_defect_pairs.py`：主脚本（代码内配置）

## 配置
打开 `copy_defect_pairs.py` 顶部“配置区”修改：

- `SRC_ROOT`：源根目录（递归遍历）
- `OUT_ROOT`：输出根目录（保留与源目录相同的相对路径结构，不再按缺陷建子目录）
- `DEFECTS`：要筛选的缺陷名称列表（如 `['裂纹','崩边']`）
- `TOTAL_LIMIT`：全局最多复制的图片-JSON对数量（命中任一缺陷即复制，且每张图片仅复制一次）
- `IMAGE_EXTS`：图片后缀列表；设为 `None` 使用默认（`.jpg .jpeg .png .bmp .tif .tiff`）
- `OVERWRITE`：若目标已存在同名文件是否覆盖（`False` 时自动添加 `_1`, `_2` 后缀）
- `CASE_INSENSITIVE`：缺陷名匹配是否大小写不敏感
- `DRY_RUN`：演练模式；为 `True` 时只打印将要复制的目标路径，不实际复制

示例：
```python
SRC_ROOT = r"D:\\data\\root"
OUT_ROOT = r"D:\\out\\picked"
DEFECTS = ["裂纹", "崩边"]
TOTAL_LIMIT = 200
IMAGE_EXTS = None  # 使用默认
OVERWRITE = False
CASE_INSENSITIVE = False
DRY_RUN = False
```

## 运行
```bash
python 7-复制图片文件/copy_defect_pairs.py
```

## 行为说明
- 仅当同名图片与 `.json` 同时存在时才认为是一对并参与筛选。
- 从 JSON 的 `shapes` 数组读取 `label` 字段判断缺陷名；支持字符串或列表两种情况。
- 命中任一缺陷即复制该对文件；同一图片只复制一次，不再因其他缺陷重复复制。
- 复制路径为 `OUT_ROOT/相对源目录路径/文件名`，例如源 `SRC_ROOT\a\b\c.jpg` -> `OUT_ROOT\a\b\c.jpg`。
- 达到 `TOTAL_LIMIT` 即停止复制。
- `OVERWRITE=False` 时为避免冲突会在文件名后添加序号（如 `_1`）。

## 注意
- 请确保 JSON 文件编码为 UTF-8，且结构中包含 `shapes` 与 `label`。
- Windows 路径请使用原始字符串（前缀 `r"..."`）或双反斜杠进行转义。 