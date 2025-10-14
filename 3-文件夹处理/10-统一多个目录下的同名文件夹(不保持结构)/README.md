# 复制前缀图片（按名称匹配，输出到当天日期目录）

在多个源根目录中查找名称匹配“单个大写字母 + 单个数字”（如 `A1`, `B2`）的文件夹，并将这些文件夹及其全部内容复制到目标根目录的当天日期目录下：
- 结构：`OUT_ROOT/YYYYMMDD/<匹配名>`（如 `.../20250903/A1`）
- 不保留源根与匹配名之间的中间路径层级
- 若目标存在同名目录，直接合并覆盖

## 文件
- `copy_prefixed_folders.py`：主脚本（代码内配置）

## 配置
在 `copy_prefixed_folders.py` 顶部设置：
- `ROOT_DIRS`：多个源根路径列表
- `OUT_ROOT`：输出根目录（脚本会自动创建 `YYYYMMDD` 子目录）
- `RECURSIVE`：是否递归查找
- `DRY_RUN`：演练模式，不实际复制

示例：
```python
ROOT_DIRS = [
    r"D:\\data\\root1",
    r"D:\\data\\root2",
]
OUT_ROOT = r"D:\\out\\prefixed_folders"
RECURSIVE = True
DRY_RUN = False
```

## 运行
```bash
python 10-复制前缀图片/copy_prefixed_folders.py
```

## 行为说明
- 匹配规则使用正则 `^[A-Z][0-9]$`。
- 输出目录层级为两层：日期/匹配名（例如 `20250903/A1`）。
- 同名目录将被合并覆盖，不追加后缀。
- `DRY_RUN=True` 时仅打印复制计划，便于确认。 