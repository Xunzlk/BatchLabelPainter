#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方框位置确定工具
帮助用户通过鼠标点击确定背景图片中文字方框的位置和大小
"""

import json
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import messagebox, filedialog
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextBoxFinder:
    """文字方框位置确定工具类"""
    
    def __init__(self):
        """初始化工具"""
        self.root = tk.Tk()
        self.root.title("方框位置确定工具")
        self.root.geometry("800x600")
        
        self.image_path = "img/background.png"
        self.config_path = "config.json"
        
        self.canvas = None
        self.image = None
        self.photo = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.current_rect = None
        
        self.setup_ui()
        self.load_image()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="选择背景图片", command=self.select_image)
        file_menu.add_command(label="保存配置", command=self.save_config)
        
        # 创建工具栏
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        tk.Label(toolbar, text="使用说明：按住鼠标左键拖拽选择文字方框区域").pack(side=tk.LEFT)
        
        tk.Button(toolbar, text="重置", command=self.reset_selection).pack(side=tk.RIGHT, padx=5)
        tk.Button(toolbar, text="保存配置", command=self.save_config).pack(side=tk.RIGHT, padx=5)
        
        # 创建画布
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        # 状态栏
        self.status_bar = tk.Label(self.root, text="请选择背景图片", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def select_image(self):
        """选择背景图片"""
        file_path = filedialog.askopenfilename(
            title="选择背景图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.image_path = file_path
            self.load_image()
    
    def load_image(self):
        """加载背景图片"""
        try:
            self.image = Image.open(self.image_path)
            
            # 计算缩放比例以适应画布
            canvas_width = 750
            canvas_height = 500
            
            img_width, img_height = self.image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            self.scale = min(scale_x, scale_y, 1.0)  # 不放大，只缩小
            
            # 缩放图片
            new_width = int(img_width * self.scale)
            new_height = int(img_height * self.scale)
            
            display_image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(display_image)
            
            # 在画布上显示图片
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            
            self.status_bar.config(text=f"图片已加载: {self.image_path} (缩放比例: {self.scale:.2f})")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败: {e}")
            logger.error(f"加载图片失败: {e}")
    
    def on_mouse_press(self, event):
        """鼠标按下事件"""
        self.start_x = event.x
        self.start_y = event.y
        
        # 删除之前的矩形
        if self.rect_id:
            self.canvas.delete(self.rect_id)
    
    def on_mouse_drag(self, event):
        """鼠标拖拽事件"""
        if self.start_x is not None and self.start_y is not None:
            # 删除之前的矩形
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            
            # 绘制新的矩形
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=2, fill='', stipple='gray50'
            )
    
    def on_mouse_release(self, event):
        """鼠标释放事件"""
        if self.start_x is not None and self.start_y is not None:
            # 计算矩形坐标（确保左上角坐标小于右下角坐标）
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)
            
            # 转换为原图坐标
            orig_x1 = int(x1 / self.scale)
            orig_y1 = int(y1 / self.scale)
            orig_x2 = int(x2 / self.scale)
            orig_y2 = int(y2 / self.scale)
            
            width = orig_x2 - orig_x1
            height = orig_y2 - orig_y1
            
            self.current_rect = {
                "x": orig_x1,
                "y": orig_y1,
                "width": width,
                "height": height
            }
            
            self.status_bar.config(
                text=f"选择区域: x={orig_x1}, y={orig_y1}, 宽度={width}, 高度={height}"
            )
    
    def reset_selection(self):
        """重置选择"""
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
        self.current_rect = None
        self.status_bar.config(text="选择已重置")
    
    def save_config(self):
        """保存配置"""
        if not self.current_rect:
            messagebox.showwarning("警告", "请先选择文字方框区域")
            return
        
        try:
            # 读取现有配置或创建默认配置
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except FileNotFoundError:
                config = {
                    "background_image": "img/background.png",
                    "font_path": "font/BitTrip7(sRB).TTF",
                    "excel_file": "data/UserIds.xlsx",
                    "output_dir": "output",
                    "text_box": {
                        "x": 100,
                        "y": 100,
                        "width": 300,
                        "height": 80
                    },
                    "font_settings": {
                        "color": [0, 0, 0],
                        "max_font_size": 48,
                        "min_font_size": 12
                    },
                    "text_alignment": "center",
                    "padding": 10
                }
            
            # 更新方框配置
            config["text_box"] = self.current_rect
            
            # 保存配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("成功", f"配置已保存到 {self.config_path}")
            logger.info(f"配置已保存: {self.current_rect}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
            logger.error(f"保存配置失败: {e}")
    
    def run(self):
        """运行工具"""
        self.root.mainloop()


def main():
    """主函数"""
    app = TextBoxFinder()
    app.run()


if __name__ == "__main__":
    main()