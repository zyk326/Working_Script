# 筛选图片对或单项（保留原结构）

该工具支持从多个根路径中递归查找名称为“单个大写字母+单个数字”（如 `A1`、`B1`）的目录，并按指定模式处理：
- 图片对模式（pair）：复制/剪切图片与同名 JSON 文件
- 单项模式（single）：仅复制/剪切没有同名 JSON 的图片

结果将保存到指定输出根目录下，并保持相对于各自源根路径的目录结构。

## 文件
- `filter_pairs_or_singles.py`：主脚本（代码内配置）

## 配置
打开脚本顶部配置区：
- `ROOT_DIRS`：多个源根路径（列表）
- `OUT_ROOT`：输出根目录（将保留相对结构）
- `MOVE_INSTEAD_OF_COPY`：是否剪切代替复制（`True`=剪切/移动，`False`=复制）
- `PROCESS_TARGET`：`"pair"`=处理图片对；`"single"`=处理单个图片
- `IMAGE_EXTS`：识别的图片后缀
- `DRY_RUN`：试运行，不实际执行
- `RECURSIVE`：是否递归

示例：
```python
ROOT_DIRS = [
    r"Y:\\data\\root1",
    r"Y:\\data\\root2",
]
OUT_ROOT = r"D:\\out\\filtered"
MOVE_INSTEAD_OF_COPY = False   # 复制
PROCESS_TARGET = "pair"       # 处理图片对
DRY_RUN = False
RECURSIVE = True
```

## 运行
```bash
python 11-筛选图片对或单项/filter_pairs_or_singles.py
```

## 行为说明
- 匹配的目录名遵循正则：`^[A-Z][0-9]$`
- 保留相对路径：源 `ROOT_DIRS[i]` 下的 `...\X\A1` 会输出到 `OUT_ROOT\...\X\A1`
- 图片对模式：复制/剪切 `image.ext` 与 `image.json`
- 单项模式：仅复制/剪切没有对应 `image.json` 的 `image.ext`
- 复制为覆盖写入；剪切为移动文件
- `DRY_RUN=True` 时仅打印计划

## 注意
- 剪切模式会移动源文件，请谨慎操作
- 确保有对源和目标目录的读写权限
- JSON 文件需与图片同名且位于同一目录 