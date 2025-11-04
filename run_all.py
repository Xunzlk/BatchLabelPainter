#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
总控入口（RunAll）

功能：
- 自动检查配置文件中的文字方框（text_box）是否有效；若无效，则先启动方框定位工具（FindTextBox），等待用户保存配置后再继续。
- 在文字方框有效时，自动启动主程序（BatchIdFill）进行批量图片生成。

兼容运行：
- 打包为 exe 后：与 FindTextBox.exe、BatchIdFill.exe 位于同一目录时，直接调用对应 .exe。
- 源码运行：如果没有 .exe，则回退调用对应的 .py 脚本（使用当前 Python 解释器）。
"""

import json
import os
import sys
import subprocess


def get_base_dir() -> str:
    """获取运行基准目录
    - 若为打包后的 exe，返回 exe 所在目录
    - 若为源码运行，返回脚本所在目录
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def load_config(config_path: str) -> dict:
    """读取 config.json 配置文件
    - 若文件不存在或解析失败，返回空字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] 无法读取配置文件: {config_path}，错误: {e}")
        return {}


def is_text_box_valid(cfg: dict) -> tuple[bool, str]:
    """校验文字方框设置 text_box 是否有效
    - 要求存在 x, y, width, height 四个字段
    - width 和 height 必须为正数
    返回 (是否有效, 失败原因)
    """
    tb = cfg.get('text_box')
    if not isinstance(tb, dict):
        return False, "text_box 不存在或不是字典"
    for key in ('x', 'y', 'width', 'height'):
        if key not in tb:
            return False, f"text_box 缺少字段: {key}"
    try:
        w = float(tb.get('width'))
        h = float(tb.get('height'))
        if w <= 0 or h <= 0:
            return False, "text_box 的 width/height 必须为正数"
    except Exception:
        return False, "text_box 的 width/height 必须为数值"
    return True, "OK"


def resolve_program_paths(base_dir: str) -> dict:
    """解析可执行文件与脚本路径
    - 优先使用同目录下的 .exe
    - 若 .exe 不存在则回退到源码 .py
    返回字典：{'find_exe','fill_exe','find_py','fill_py'}
    """
    return {
        'find_exe': os.path.join(base_dir, 'FindTextBox.exe'),
        'fill_exe': os.path.join(base_dir, 'BatchIdFill.exe'),
        'find_py': os.path.join(base_dir, 'find_text_box.py'),
        'fill_py': os.path.join(base_dir, 'id_fill_generator.py'),
    }


def run_find_text_box(paths: dict) -> int:
    """运行方框定位工具
    - 若存在 .exe 则运行 .exe
    - 否则使用当前 Python 解释器运行 .py
    返回进程退出码
    """
    if os.path.exists(paths['find_exe']):
        print("[INFO] 启动 FindTextBox.exe 进行文字方框设置...")
        result = subprocess.run([paths['find_exe']], cwd=os.path.dirname(paths['find_exe']))
        return result.returncode
    elif os.path.exists(paths['find_py']):
        print("[INFO] 未找到 FindTextBox.exe，回退运行 find_text_box.py...")
        result = subprocess.run([sys.executable, paths['find_py']], cwd=os.path.dirname(paths['find_py']))
        return result.returncode
    else:
        print("[ERROR] 未找到方框定位工具（FindTextBox.exe 或 find_text_box.py）")
        return 1


def run_batch_fill(paths: dict) -> int:
    """运行批量生成主程序
    - 若存在 .exe 则运行 .exe
    - 否则使用当前 Python 解释器运行 .py
    返回进程退出码
    """
    if os.path.exists(paths['fill_exe']):
        print("[INFO] 启动 BatchIdFill.exe 进行批量图片生成...")
        result = subprocess.run([paths['fill_exe']], cwd=os.path.dirname(paths['fill_exe']))
        return result.returncode
    elif os.path.exists(paths['fill_py']):
        print("[INFO] 未找到 BatchIdFill.exe，回退运行 id_fill_generator.py...")
        result = subprocess.run([sys.executable, paths['fill_py']], cwd=os.path.dirname(paths['fill_py']))
        return result.returncode
    else:
        print("[ERROR] 未找到批量生成主程序（BatchIdFill.exe 或 id_fill_generator.py）")
        return 1


def main():
    """总控流程
    1) 加载配置并校验文字方框
    2) 若方框无效：运行 FindTextBox，等待用户设置后再次校验
    3) 方框有效：运行 BatchIdFill 生成图片
    """
    base_dir = get_base_dir()
    config_path = os.path.join(base_dir, 'config.json')
    paths = resolve_program_paths(base_dir)

    print("=== 总控入口（RunAll）启动 ===")
    print(f"[INFO] 基准目录: {base_dir}")
    print(f"[INFO] 配置文件: {config_path}")

    cfg = load_config(config_path)
    valid, reason = is_text_box_valid(cfg)
    if not valid:
        print(f"[WARN] 文字方框配置无效：{reason}")
        rc = run_find_text_box(paths)
        if rc != 0:
            print(f"[ERROR] 方框定位工具运行失败，退出码: {rc}")
            sys.exit(rc)

        # 再次读取配置并校验
        cfg = load_config(config_path)
        valid, reason = is_text_box_valid(cfg)
        if not valid:
            print(f"[ERROR] 方框仍未正确配置：{reason}。请重新运行并在 FindTextBox 中保存配置。")
            sys.exit(2)

    # 运行主程序生成图片
    rc = run_batch_fill(paths)
    if rc != 0:
        print(f"[ERROR] 批量生成程序运行失败，退出码: {rc}")
        sys.exit(rc)

    print("=== 全流程完成，已生成图片到 output 目录 ===")


if __name__ == '__main__':
    main()