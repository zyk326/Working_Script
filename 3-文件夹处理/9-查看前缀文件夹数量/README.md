# 查看前缀文件夹（大写字母+数字）

本工具用于统计给定目录下，名称符合“单个大写英文字母 + 单个数字”（例如 `A1`, `B2`）的文件夹，输出数量与完整路径。现已支持多个根路径。

## 文件
- `find_prefixed_folders.py`：脚本（代码内配置）

## 配置
打开 `find_prefixed_folders.py` 顶部修改：
- `ROOT_DIRS`：根路径列表，按顺序遍历
- `RECURSIVE`：是否递归子目录查找（`True` 为所有层级，`False` 仅第一层）

命名规则使用正则：`^[A-Z][0-9]$`

示例：
```python
ROOT_DIRS = [
    r"D:\\data\\root1",
    r"D:\\data\\root2",
]
RECURSIVE = False
```

## 运行
```bash
python 9-查看前缀文件夹/find_prefixed_folders.py
```

## 输出
- 每个根路径下的匹配数量与详细路径列表
- 最后输出总匹配文件夹数量（合计） 