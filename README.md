# ID填充图片生成器

这个工具可以从Excel文件中读取用户ID，并将其填充到背景图片的指定方框中，支持自适应字体大小。

## 功能特点

- 从Excel文件读取用户ID数据
- 自动调整字体大小以适应方框
- 支持中文、英文和特殊字符
- 批量生成图片
- 可配置的方框位置和样式
- 图形化工具辅助确定方框位置

## 文件结构

```
BatchIdFill/
├── data/
│   └── UserIds.xlsx          # 用户ID数据文件
├── font/
│   └── BitTrip7(sRB).TTF     # 字体文件
├── img/
│   └── background.png        # 背景图片
├── output/                   # 输出目录（自动创建）
├── config.json              # 配置文件
├── id_fill_generator.py     # 主程序
├── find_text_box.py         # 方框位置确定工具
├── test_alignment.py        # 对齐与边界检测测试脚本（生成带辅助线的测试图片）
├── requirements.txt         # 依赖包列表
└── README.md               # 说明文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用步骤

### 1. 确定方框位置（首次使用）

运行方框位置确定工具：

```bash
python find_text_box.py
```

- 在打开的窗口中，用鼠标拖拽选择文字应该显示的方框区域
- 点击"保存配置"按钮保存方框位置到配置文件

### 2. 调整配置（可选）

编辑 `config.json` 文件来调整各种参数：

```json
{
    "background_image": "img/background.png",    // 背景图片路径
    "font_path": "font/BitTrip7(sRB).TTF",      // 字体文件路径
    "excel_file": "data/UserIds.xlsx",          // Excel文件路径
    "output_dir": "output",                     // 输出目录
    "text_box": {                               // 文字方框设置
        "x": 100,                               // 方框左上角X坐标
        "y": 100,                               // 方框左上角Y坐标
        "width": 300,                           // 方框宽度
        "height": 80                            // 方框高度
    },
    "font_settings": {                          // 字体设置
        "color": [0, 0, 0],                     // 字体颜色 [R, G, B]
        "max_font_size": 48,                    // 最大字体大小
        "min_font_size": 12,                    // 最小字体大小
        "bold": false,                          // 是否加粗（true/false）。开启后默认使用 1px 描边模拟加粗
        "stroke_width": 0,                      // 描边宽度（像素）。当与 color 相同可模拟加粗；推荐 0~2
        "stroke_color": [0, 0, 0]               // 描边颜色 [R, G, B]，未配置时默认与 color 相同
    },
    "text_alignment": "center",                 // 文字对齐方式: center/left/right
    "padding": 10                               // 方框内边距
}
```

### 3. 准备数据

确保Excel文件格式正确：
- 第一行为标题（如"ID"）
- 从第二行开始为用户ID数据
- ID应该在第一列（A列）

### 4. 生成图片

运行主程序：

```bash
python id_fill_generator.py
```

程序会：
- 读取Excel文件中的所有用户ID
- 为每个ID生成一张图片
- 自动调整字体大小以适应方框
- 将生成的图片保存到output目录

### 5. 对齐测试（可选）

若需验证文字的水平与垂直居中效果，可运行对齐测试脚本：

```bash
python test_alignment.py
```

脚本会在背景图上绘制：
- 红色矩形：文字方框边界
- 绿色水平线：方框垂直居中参考线
- 绿色垂直线：方框水平居中参考线

并生成多组不同长度文字的测试图片，文件保存在 `output/` 目录下：
- `output/test_alignment_1_*.png`
- `output/test_alignment_2_*.png`
- `output/test_alignment_3_*.png`

这些图片可帮助你直观检查：
- 水平居中是否准确（文字中心与垂直参考线重合）
- 垂直居中是否准确（文字基线区域与水平参考线对称）

## 配置说明

### 方框位置设置
- `x`, `y`: 方框左上角在背景图片中的坐标（像素）
- `width`, `height`: 方框的宽度和高度（像素）

### 字体设置
- `color`: RGB颜色值，例如 [0, 0, 0] 表示黑色，[255, 0, 0] 表示红色
- `max_font_size`: 最大字体大小，程序会从这个大小开始尝试
- `min_font_size`: 最小字体大小，如果文字太长会缩小到这个大小
- `bold`: 是否加粗（布尔值）。开启后会自动将 `stroke_width` 设为 1（若你未显式配置），并在绘制时使用与 `color` 相同的描边颜色来模拟加粗
- `stroke_width`: 描边宽度（像素）。当与 `color` 相同可模拟加粗；注意描边会增加文字的实际宽高，程序已在尺寸计算中考虑该影响
- `stroke_color`: 描边颜色（RGB）。如果未设置此项，程序会使用与 `color` 相同的颜色作为描边颜色；如需“彩色描边 + 不同填充色”效果，配置此项即可。

### 对齐方式
- `center`: 居中对齐
- `left`: 左对齐
- `right`: 右对齐

## 注意事项

1. 确保字体文件存在且可读
2. 背景图片建议使用PNG格式以支持透明度
3. Excel文件应该使用UTF-8编码以正确显示中文
4. 生成的图片会保存为PNG格式
5. 如果用户ID包含特殊字符，文件名会自动转换为安全字符

## 故障排除

### 常见问题

1. **字体加载失败**
   - 检查字体文件路径是否正确
   - 确保字体文件存在且可读

2. **Excel读取失败**
   - 检查Excel文件路径是否正确
   - 确保Excel文件格式正确（第一列包含ID数据）

3. **图片生成失败**
   - 检查背景图片是否存在
   - 确保输出目录有写入权限

4. **文字显示不完整**
   - 调整方框大小（增加width或height）
   - 调整最小字体大小（减小min_font_size）
   - 减少内边距（padding）
   - 若启用了加粗（bold/stroke_width>0），可以适当减小 `stroke_width` 或字体大小

### 日志信息

程序运行时会显示详细的日志信息，包括：
- 配置加载状态
- Excel数据读取结果
- 图片生成进度
- 错误信息

## 示例

假设你的Excel文件包含以下用户ID：
- Amorta
- Luks
- aliks devil
- no one
- showmaker
- ももちゃん

程序会生成对应的图片文件：
- Amorta_001.png
- Luks_002.png
- aliks_devil_003.png
- no___one_004.png
- showmaker_005.png
- ももちゃん_006.png

每张图片都包含背景图和对应的用户ID文字。