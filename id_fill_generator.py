"""
ID填充图片生成器
从Excel文件读取用户ID，并将其填充到背景图片的指定方框中
支持自适应字体大小，确保文字完整显示且不超出方框
"""

import os
import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IDFillGenerator:
    """ID填充图片生成器类"""
    
    def __init__(self, config_path='config.json'):
        """
        初始化生成器
        
        Args:
            config_path (str): 配置文件路径
        """
        self.config = self.load_config(config_path)
        self.font_path = self.config['font_path']
        self.background_path = self.config['background_image']
        self.excel_path = self.config['excel_file']
        self.output_dir = self.config['output_dir']
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_config(self, config_path):
        """
        加载配置文件
        
        Args:
            config_path (str): 配置文件路径
            
        Returns:
            dict: 配置信息
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
    
    def read_excel_data(self):
        """
        从Excel文件读取用户ID数据
        
        Returns:
            list: 用户ID列表
        """
        try:
            df = pd.read_excel(self.excel_path)
            # 假设ID在第一列，跳过标题行
            ids = df.iloc[1:, 0].dropna().tolist()
            logger.info(f"成功读取 {len(ids)} 个用户ID")
            return ids
        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            raise
    
    def calculate_font_size(self, text, font_path, max_width, max_height, max_font_size, min_font_size, stroke_width=0):
        """
        计算合适的字体大小，确保文字完整显示且不超出方框
        
        Args:
            text (str): 要显示的文字
            font_path (str): 字体文件路径
            max_width (int): 方框最大宽度
            max_height (int): 方框最大高度
            max_font_size (int): 最大字体大小
            min_font_size (int): 最小字体大小
            stroke_width (int): 文字描边宽度，用于模拟加粗效果（同时会影响文字的实际宽高）
        
        Returns:
            int: 合适的字体大小
        """
        font_size = max_font_size
        
        while font_size >= min_font_size:
            try:
                font = ImageFont.truetype(font_path, font_size)
                
                # 使用更准确的方法计算文字尺寸
                # 创建临时图像来测量文字实际占用空间
                temp_img = Image.new('RGB', (max_width * 2, max_height * 2), 'white')
                temp_draw = ImageDraw.Draw(temp_img)
                
                # 获取文字边界框
                # 在测量时考虑描边宽度，确保加粗后仍可正确计算
                bbox = temp_draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 获取字体度量信息，用于更准确的高度计算
                ascent, descent = font.getmetrics()
                actual_height = ascent + descent
                
                # 添加一些安全边距（3%）
                safe_width = text_width * 1.03
                # 当存在描边时，text_height 已包含描边，直接使用更可靠
                safe_height = max(text_height, actual_height) * 1.03
                
                # 检查是否适合方框
                if safe_width <= max_width and safe_height <= max_height:
                    logger.debug(f"字体大小 {font_size}: 文字尺寸 {safe_width:.1f}x{safe_height:.1f}, 方框尺寸 {max_width}x{max_height}")
                    return font_size
                    
                font_size -= 1  # 更精细的调整步长
            except Exception as e:
                logger.warning(f"字体大小计算出错: {e}")
                font_size -= 2
        
        logger.warning(f"使用最小字体大小 {min_font_size} 对于文字: {text}")
        return min_font_size

    def is_ascii_text(self, text):
        """
        判断文本是否全部为 ASCII 字符。

        说明：
        - 优先使用 Python 3.7+ 的 str.isascii() 方法。
        - 若不可用或异常，则回退到逐字符检查码点 < 128。

        Args:
            text (str): 需要判断的文本

        Returns:
            bool: True 表示全部为 ASCII；False 表示包含非 ASCII 字符
        """
        try:
            return str(text).isascii()
        except Exception:
            return all(ord(ch) < 128 for ch in str(text))

    def get_font_settings_for_text(self, text):
        """
        根据文本类型（英文/非英文）返回合并后的字体设置。

        合并规则：
        - 以全局 font_settings 作为基础。
        - 英文文本（ASCII）时，使用 font_settings_latin 覆盖基础设置。
        - 非英文文本（包含非 ASCII）时，使用 font_settings_non_latin 覆盖基础设置。
        - 若覆盖项未配置，则使用基础设置。
        - 当 bold=True 且未显式设置 stroke_width 或为 0 时，默认将 stroke_width 设为 1。
        - 若未显式设置 stroke_color，则默认与 color 相同。

        Args:
            text (str): 需要绘制的文本

        Returns:
            dict: 合并后的字体设置字典（包含 color/max_font_size/min_font_size/bold/stroke_width/stroke_color）
        """
        base = dict(self.config.get('font_settings', {}))
        is_ascii = self.is_ascii_text(text)
        overrides = self.config.get('font_settings_latin') if is_ascii else self.config.get('font_settings_non_latin')
        if overrides:
            base.update(overrides)

        # 处理加粗默认描边
        sw = int(base.get('stroke_width', 0) or 0)
        if base.get('bold', False) and sw == 0:
            sw = 1
        base['stroke_width'] = sw

        # 默认描边颜色与文字颜色一致
        if 'stroke_color' not in base or base.get('stroke_color') is None:
            base['stroke_color'] = base.get('color')

        return base

    def choose_font_path(self, text):
        """
        根据文本内容选择字体路径。

        规则：
        - 若文本全部为 ASCII 字符（英文、数字、常见符号、空格等），使用配置中的 font_path_latin
        - 否则（包含非 ASCII 字符，例如中文、日文、韩文等），使用配置中的 font_path_non_latin
        - 若未配置上述两项，则回退使用 font_path

        Args:
            text (str): 需要绘制的文本

        Returns:
            str: 选择后的字体文件路径
        """
        try:
            # 优先使用专用配置项
            font_path_latin = self.config.get('font_path_latin')
            font_path_non_latin = self.config.get('font_path_non_latin')

            is_ascii = self.is_ascii_text(text)

            if is_ascii and font_path_latin:
                return font_path_latin
            if (not is_ascii) and font_path_non_latin:
                return font_path_non_latin

            # 回退到默认字体路径
            return self.font_path
        except Exception as e:
            logger.warning(f"字体选择失败，回退默认字体: {e}")
            return self.font_path
    
    def create_id_image(self, user_id, output_filename):
        """
        为单个用户ID创建图片
        
        Args:
            user_id (str): 用户ID
            output_filename (str): 输出文件名
        """
        try:
            # 打开背景图片
            background = Image.open(self.background_path).convert('RGBA')
            
            # 创建绘图对象
            draw = ImageDraw.Draw(background)
            
            # 获取配置参数
            text_box = self.config['text_box']
            # 根据文本类型（英文/非英文）合并并获取字体设置
            font_settings = self.get_font_settings_for_text(str(user_id))
            padding = self.config['padding']
            
            # 计算实际可用空间（减去内边距）
            available_width = text_box['width'] - 2 * padding
            available_height = text_box['height'] - 2 * padding

            # 读取加粗/描边配置（已在 font_settings 中处理默认值）
            stroke_width = font_settings.get('stroke_width', 0)

            # 根据文本内容选择字体路径（英文/非英文）
            selected_font_path = self.choose_font_path(str(user_id))

            # 计算合适的字体大小
            font_size = self.calculate_font_size(
                str(user_id),
                selected_font_path,
                available_width,
                available_height,
                font_settings['max_font_size'],
                font_settings['min_font_size'],
                stroke_width=stroke_width
            )
            
            # 创建字体对象
            font = ImageFont.truetype(selected_font_path, font_size)
            
            # 使用更准确的方法获取文字尺寸和位置
            # 创建临时绘图对象来测量文字
            temp_img = Image.new('RGB', (text_box['width'], text_box['height']), 'white')
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 获取文字边界框（相对于(0,0)位置）
            bbox = temp_draw.textbbox((0, 0), str(user_id), font=font, stroke_width=stroke_width)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 获取字体的度量信息
            ascent, descent = font.getmetrics()
            total_font_height = ascent + descent

            # 计算文字位置（使用 Pillow anchor 实现更稳定的居中/对齐）
            # 说明：
            # - 当存在描边(stroke)时，文字的视觉边界会随 stroke 增加，
            #   使用 anchor='mm'/'lm'/'rm' 以边界框为参考点进行定位，可确保居中稳定。
            if self.config['text_alignment'] == 'center':
                # 中心点坐标（方框中心）
                text_x = text_box['x'] + text_box['width'] // 2
                text_y = text_box['y'] + text_box['height'] // 2
                anchor = 'mm'
            elif self.config['text_alignment'] == 'left':
                # 左对齐并垂直居中（使用中线作为 anchor 的垂直参考）
                text_x = text_box['x'] + padding
                text_y = text_box['y'] + text_box['height'] // 2
                anchor = 'lm'
            else:  # right
                # 右对齐并垂直居中
                text_x = text_box['x'] + text_box['width'] - padding
                text_y = text_box['y'] + text_box['height'] // 2
                anchor = 'rm'
            
            # 绘制文字
            # 读取描边颜色（若未配置则与文字颜色一致，已在 font_settings 默认处理）
            stroke_color = font_settings.get('stroke_color', font_settings['color'])

            draw.text(
                (text_x, text_y),
                str(user_id),
                font=font,
                fill=tuple(font_settings['color']),
                stroke_width=stroke_width,
                stroke_fill=tuple(stroke_color),
                anchor=anchor
            )
            
            # 保存图片
            output_path = os.path.join(self.output_dir, output_filename)
            background.save(output_path, 'PNG')
            logger.info(f"成功生成图片: {output_path}")
            
        except Exception as e:
            logger.error(f"生成图片失败 ({user_id}): {e}")
            raise
    
    def generate_all_images(self):
        """
        为所有用户ID生成图片
        """
        try:
            # 读取用户ID数据
            user_ids = self.read_excel_data()
            
            logger.info(f"开始生成 {len(user_ids)} 张图片...")
            
            # 为每个用户ID生成图片
            for i, user_id in enumerate(user_ids, 1):
                # 清理文件名中的特殊字符
                safe_filename = str(user_id).replace(' ', '_').replace('/', '_').replace('\\', '_')
                output_filename = f"{safe_filename}_{i:03d}.png"
                
                self.create_id_image(user_id, output_filename)
                
                # 显示进度
                if i % 10 == 0 or i == len(user_ids):
                    logger.info(f"进度: {i}/{len(user_ids)} ({i/len(user_ids)*100:.1f}%)")
            
            logger.info(f"所有图片生成完成！输出目录: {self.output_dir}")
            
        except Exception as e:
            logger.error(f"批量生成图片失败: {e}")
            raise


def main():
    """主函数"""
    try:
        # 创建生成器实例
        generator = IDFillGenerator()
        
        # 生成所有图片
        generator.generate_all_images()
        
        print("=== 图片生成完成 ===")
        print(f"输出目录: {generator.output_dir}")
        print("请检查生成的图片，如需调整方框位置或字体设置，请修改 config.json 文件")
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        print(f"错误: {e}")
        print("请检查配置文件和输入文件是否正确")


if __name__ == "__main__":
    main()