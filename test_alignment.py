"""
测试字体对齐和边界检测效果的脚本
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_image():
    """
    创建一个测试图片，显示方框边界和文字对齐效果

    将根据文本是否为 ASCII，动态选择英文字体或非英文字体，
    以验证不同字体下的居中/对齐在加粗场景下是否仍然稳定。
    """
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 打开背景图片
    background = Image.open(config['background_image']).convert('RGBA')
    draw = ImageDraw.Draw(background)
    
    # 获取配置参数
    text_box = config['text_box']
    font_settings_global = config['font_settings']

    def is_ascii_text(s):
        """
        判断文本是否为 ASCII（与主程序保持一致的逻辑）。
        优先使用 str.isascii()，否则回退逐字符码点检查。
        """
        try:
            return str(s).isascii()
        except Exception:
            return all(ord(ch) < 128 for ch in str(s))

    def get_selected_font_settings(is_ascii):
        """
        根据是否 ASCII 返回合并后的字体设置（全局 + 针对英文/非英文的覆盖）。
        - 当 bold=True 且 stroke_width 缺省或为 0 时，默认 stroke_width=1。
        - 当 bold=False 时，无论配置如何，强制 stroke_width=0。
        - 未设置 stroke_color 时，默认与 color 相同。
        """
        selected = dict(font_settings_global)
        overrides = config.get('font_settings_latin') if is_ascii else config.get('font_settings_non_latin')
        if overrides:
            selected.update(overrides)
        if not selected.get('bold', False):
            selected['stroke_width'] = 0
        else:
            sw = int(selected.get('stroke_width', 0) or 0)
            if sw == 0:
                sw = 1
            selected['stroke_width'] = sw
        if 'stroke_color' not in selected or selected.get('stroke_color') is None:
            selected['stroke_color'] = selected.get('color')
        return selected
    
    # 绘制方框边界（红色虚线）
    box_x = text_box['x']
    box_y = text_box['y']
    box_width = text_box['width']
    box_height = text_box['height']
    
    # 绘制方框轮廓
    draw.rectangle(
        [box_x, box_y, box_x + box_width, box_y + box_height],
        outline=(255, 0, 0, 128),  # 红色半透明
        width=3
    )
    
    # 绘制中心线（帮助检查垂直居中）
    center_y = box_y + box_height // 2
    draw.line(
        [box_x, center_y, box_x + box_width, center_y],
        fill=(0, 255, 0, 128),  # 绿色半透明
        width=2
    )
    
    # 绘制垂直中心线（帮助检查水平居中）
    center_x = box_x + box_width // 2
    draw.line(
        [center_x, box_y, center_x, box_y + box_height],
        fill=(0, 255, 0, 128),  # 绿色半透明
        width=2
    )
    
    # 测试不同长度的文字
    test_texts = ["short", "medium length", "very long text and more", "ももちゃん", "悟空"]
    
    for i, test_text in enumerate(test_texts):
        # 为每个测试文字创建单独的图片
        test_img = background.copy()
        test_draw = ImageDraw.Draw(test_img)
        
        # 计算字体大小
        # 读取加粗/描边配置（与主程序保持一致）
        is_ascii = is_ascii_text(test_text)
        selected_settings = get_selected_font_settings(is_ascii)
        stroke_width = selected_settings.get('stroke_width', 0)

        # 根据文本内容选择字体路径（英文/非英文）
        selected_font_path = None
        try:
            selected_font_path = config.get('font_path_latin') if is_ascii else config.get('font_path_non_latin', config['font_path'])
        except Exception:
            selected_font_path = config['font_path']

        font_size = calculate_font_size(
            test_text,
            selected_font_path,
            box_width - 2 * config['padding'],
            box_height - 2 * config['padding'],
            selected_settings['max_font_size'],
            selected_settings['min_font_size'],
            stroke_width=stroke_width
        )
        
        # 创建字体
        font = ImageFont.truetype(selected_font_path or config['font_path'], font_size)
        
        # 计算文字位置
        temp_img = Image.new('RGB', (box_width, box_height), 'white')
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), test_text, font=font, stroke_width=stroke_width)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 获取字体度量信息
        ascent, descent = font.getmetrics()
        total_font_height = ascent + descent
        
        # 使用 Pillow 的 anchor 实现更稳定的居中（包含描边影响）
        text_x = box_x + box_width // 2
        text_y = box_y + box_height // 2
        anchor = 'mm'
        
        # 绘制文字
        # 读取描边颜色（未配置则使用文字颜色）
        stroke_color = selected_settings.get('stroke_color', selected_settings['color'])

        test_draw.text(
            (text_x, text_y),
            test_text,
            font=font,
            fill=tuple(selected_settings['color']),
            stroke_width=stroke_width,
            stroke_fill=tuple(stroke_color),
            anchor=anchor
        )
        
        # 保存测试图片
        output_path = f"output/test_alignment_{i+1}_{test_text[:5]}.png"
        test_img.save(output_path, 'PNG')
        logger.info(f"生成测试图片: {output_path}")
        logger.info(f"文字: '{test_text}', ASCII: {is_ascii}, 字体大小: {font_size}, 位置: ({text_x}, {text_y}), anchor: {anchor}, 字体: {selected_font_path}, stroke_width: {stroke_width}")

def calculate_font_size(text, font_path, max_width, max_height, max_font_size, min_font_size, stroke_width=0):
    """
    计算合适的字体大小（与主程序相同的逻辑），支持描边宽度以模拟加粗效果
    """
    font_size = max_font_size
    
    while font_size >= min_font_size:
        try:
            font = ImageFont.truetype(font_path, font_size)
            
            # 使用更准确的方法计算文字尺寸
            temp_img = Image.new('RGB', (max_width * 2, max_height * 2), 'white')
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 获取文字边界框
            bbox = temp_draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 获取字体度量信息
            ascent, descent = font.getmetrics()
            actual_height = ascent + descent
            
            # 添加安全边距
            safe_width = text_width * 1.03
            safe_height = max(text_height, actual_height) * 1.03
            
            # 检查是否适合方框
            if safe_width <= max_width and safe_height <= max_height:
                return font_size
                
            font_size -= 1
        except Exception as e:
            logger.warning(f"字体大小计算出错: {e}")
            font_size -= 2
    
    return min_font_size

if __name__ == "__main__":
    logger.info("开始生成测试图片...")
    create_test_image()
    logger.info("测试图片生成完成！")