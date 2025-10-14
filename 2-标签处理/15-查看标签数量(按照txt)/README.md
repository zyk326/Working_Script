# YOLO 标签统计脚本

该脚本用于统计 **YOLO 格式标签数据集** 的分布情况。  
支持以下功能：
- 统计每个类别（缺陷）的 **标签数量**  
- 统计每个类别对应的 **图片数量**  
- 支持多文件夹指定或全量统计  
- 支持加载标签映射文件（编号 → 类别名）  
- 支持将结果输出到文件  

---

## 使用场景
在训练 YOLO 模型前，常常需要检查数据集是否存在：
- 类别分布是否均衡
- 是否有标签缺失
- 是否有极少数样本类别  
该脚本可以帮助快速分析标签分布情况。

---

## 文件说明
- `yolo_label_statistics.py`  
  主程序，执行统计功能。  

- `label_name.txt`  
  标签映射文件（可选），每行一个类别名称，顺序对应类别编号。  
  ```
  scratch
  dent
  missing_part
  contamination
  ...
  ```

---

## 使用方法

### 1. 修改配置
在脚本开头配置部分修改路径：
```python
# 标签文件夹路径（包含多个子文件夹）
LABEL_ROOT_PATH = r"S:\train_data_zyk\V5\VOC_Data\zyk_sim_tool\LY_B25_C\labels"

# 要统计的文件夹列表（如果为空则统计所有文件夹）
TARGET_FOLDERS = ["train_20250909_C"]  # 空列表表示统计所有文件夹

# 标签映射文件路径（可选）
LABEL_MAPPING_FILE = r"S:\train_data_zyk\V5\VOC_Data\zyk_sim_tool\LY_B25_C\label_name.txt"

# 输出结果文件路径（可选）
OUTPUT_FILE = r"S:\train_data_zyk\V5\VOC_Data\zyk_sim_tool\LY_B25_C\train_20250909_C.txt"
```

### 2. 运行脚本
```bash
python yolo_label_statistics.py
```

### 3. 输出结果
运行后会在控制台打印统计报告，并可选择保存到文件。  

示例输出：
```
============================================================
YOLO标签统计报告
============================================================

总体统计:
总标签数量: 12540
标签类别数: 4

文件夹: train_20250909_C
----------------------------------------
  0 (scratch        ):   5200 标签, 1800 图片
  1 (dent           ):   2100 标签,  900 图片
  2 (missing_part   ):   3000 标签, 1100 图片
  3 (contamination  ):   2240 标签,  950 图片

总体标签分布:
----------------------------------------
 0 (scratch        ):   5200 (41.5%)
 1 (dent           ):   2100 (16.8%)
 2 (missing_part   ):   3000 (23.9%)
 3 (contamination  ):   2240 (17.9%)
```

---

## 注意事项
1. YOLO 标签格式必须为：  
   ```
   class_id x_center y_center width height
   ```
   每行一个目标。

2. 如果不提供 `label_name.txt`，则输出结果会显示 `未知标签_x`。

3. 支持 Windows 和 Linux 系统，需 Python 3.6+。

---

## 许可证
MIT License
