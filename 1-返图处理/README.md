# 图片文件分类整理工具

这个Python脚本可以按照图片文件名中的前缀自动分类整理文件。

## 功能说明

- 自动识别图片文件名中的前缀（如 `front_001.png` 中的 `front`）
- 为每个前缀创建对应的文件夹
- 将图片文件和对应的JSON文件复制到结果目录中（不会移动原文件）
- 支持多种图片格式：PNG, JPG, JPEG, GIF, BMP
- **支持两种处理模式**：
  - 模式1：处理单个CutAIImage文件夹
  - 模式2：批量处理根目录下所有子文件夹中的CutAIImage
- **统一结果管理**：所有分类结果统一保存到指定的"结果"文件夹中

## 使用方法

1. 运行脚本：
   ```bash
   python organize_images.py
   ```

2. 选择处理模式：
   - **模式1**：处理单个CutAIImage文件夹
   - **模式2**：批量处理根目录下的所有子文件夹中的CutAIImage

3. 根据选择的模式：
   - 模式1：输入CutAIImage文件夹的路径
   - 模式2：输入根目录的路径（脚本会自动遍历所有子文件夹）

4. 确认操作后，脚本会自动完成分类整理

## 文件命名规则

脚本会识别以下格式的文件名：
- `xx_yyyy.png` → 前缀为 `xx`
- `xx_yyyy.json` → 前缀为 `xx`

其中 `xx` 是分类标识，`yyyy` 是其他信息。

## 注意事项

- 此操作会复制文件到结果目录，原文件保持不变
- 脚本会自动跳过已存在的文件夹
- 如果复制文件失败，会显示错误信息但继续处理其他文件
- 结果文件夹会自动创建在指定位置

## 示例

### 模式1：单个文件夹处理

假设有以下文件：
```
CutAIImage/
├── front_001.png
├── front_001.json
├── back_002.png
├── back_002.json
├── side_003.png
└── side_003.json
```

运行脚本后会变成：
```
CutAIImage/
├── front/
│   ├── front_001.png
│   └── front_001.json
├── back/
│   ├── back_002.png
│   └── back_002.json
└── side/
    ├── side_003.png
    └── side_003.json
```

### 模式2：批量处理多个子文件夹

假设根目录结构如下：
```
根目录/
├── 项目A/
│   └── CutAIImage/
│       ├── front_001.png
│       └── front_001.json
├── 项目B/
│   └── CutAIImage/
│       ├── back_002.png
│       └── back_002.json
└── 项目C/
    └── CutAIImage/
        ├── side_003.png
        └── side_003.json
```

运行脚本后会变成：
```
根目录/
├── 项目A/
│   └── CutAIImage/
│       ├── front_001.png
│       └── front_001.json
├── 项目B/
│   └── CutAIImage/
│       ├── back_002.png
│       └── back_002.json
├── 项目C/
│   └── CutAIImage/
│       ├── side_003.png
│       └── side_003.json
└── 结果/
    ├── front/
    │   ├── front_001.png
    │   └── front_001.json
    ├── back/
    │   ├── back_002.png
    │   └── back_002.json
    └── side/
        ├── side_003.png
        └── side_003.json
```

**注意**：原文件保持不变，分类结果统一保存在根目录下的"结果"文件夹中 