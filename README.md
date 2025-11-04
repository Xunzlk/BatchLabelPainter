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
- `bold`: 是否加粗（布尔值）。开启后会自动将 `stroke_width` 设为 1（若你未显式配置），并在绘制时使用与 `color` 相同的描边颜色来模拟加粗；当 `bold=false` 时，程序会强制将 `stroke_width` 设为 0（完全不描边）
- `stroke_width`: 描边宽度（像素）。当与 `color` 相同可模拟加粗；注意描边会增加文字的实际宽高，程序已在尺寸计算中考虑该影响；若 `bold=false`，此项将被忽略并置为 0
- `stroke_color`: 描边颜色（RGB）。如果未设置此项，程序会使用与 `color` 相同的颜色作为描边颜色；如需“彩色描边 + 不同填充色”效果，配置此项即可。

### 按语言选择字体
- 当需要区分英文与其他语言的字体时，可在 `config.json` 中额外配置：
  - `font_path_latin`: 英文字体路径（仅 ASCII 文本使用），例如 `font/BitTrip7(sRB).TTF`
  - `font_path_non_latin`: 非英文字体路径（包含中文/日文/韩文等非 ASCII 文本使用），例如 `font/ChillBitmap_16px.ttf`
- 程序会自动检测文本是否为 ASCII：
  - 仅 ASCII（英文、数字、常见符号、空格等）→ 使用 `font_path_latin`
  - 含非 ASCII（中文、日文、韩文等）→ 使用 `font_path_non_latin`
- 若未设置这两项，会回退使用 `font_path`
- 混合文本（既有英文又有非 ASCII）会使用 `font_path_non_latin`，以保证所有字符都能渲染；如需“每个字符按语言分别选择字体”的高级排版，我可以为你实现按字符切分并逐段布局的版本。

### 每种字体独立加粗与描边设置
- 在 `config.json` 中可为英文与非英文分别配置加粗与描边效果：
  - `font_settings_latin`: 针对英文（ASCII）文本的字体设置（可包含 `bold`、`stroke_width`、`stroke_color`、`max_font_size`、`min_font_size`、`color` 等任意需要覆盖的项）
  - `font_settings_non_latin`: 针对非英文（包含非 ASCII 字符）文本的字体设置（字段同上）
- 合并规则：
  - 以全局 `font_settings` 为基础；按文本类型选择对应的 `font_settings_latin` 或 `font_settings_non_latin` 覆盖基础设置
  - 当 `bold` 为 `true` 且未显式设置 `stroke_width` 或其为 0 时，程序默认 `stroke_width = 1`
  - 当 bold=False 时，无论配置如何，都强制禁用描边（stroke_width=0）。
  - 若未设置 `stroke_color`，则默认与 `color` 相同
- 示例（仅示意）：
```json
{
  "font_settings": {
    "color": [197, 253, 82],
    "max_font_size": 400,
    "min_font_size": 12,
    "bold": true,
    "stroke_width": 2
  },
  "font_settings_latin": {
    "bold": true,
    "stroke_width": 1
  },
  "font_settings_non_latin": {
    "bold": true,
    "stroke_width": 2,
    "stroke_color": [197, 253, 82]
  }
}
```

### 对齐方式
- `center`: 居中对齐
- `left`: 左对齐
- `right`: 右对齐

### 输出文件命名规则
- 文件名格式：`<三位编号>_<安全化ID>.png`
  - 示例：
    - `output/001_Xlmy.png`
    - `output/002_Luks.png`
    - `output/003_alice_devil.png`
- 编号从 001 开始，按 Excel 中的出现顺序递增，便于在文件管理器中按名称排序。
- “安全化ID”会将不适合文件名的字符转换或替换，确保跨平台可用；原始中文/日文文字仍会正确渲染到图片中（不影响图片内容显示）。

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
- Xlmy
- Luks
- aliks devil
- no one
- showmaker
- ももちゃん

程序会生成对应的图片文件：
- 001_Xlmy.png
- 002_Luks.png
- 003_aliks_devil.png
- 004_no___one.png
- 005_showmaker.png
- 006_ももちゃん.png

每张图片都包含背景图和对应的用户ID文字。