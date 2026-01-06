#!/usr/bin/env python3

import argparse

from PIL import Image, ImageDraw, ImageFont


def generate_font_bin(ttf_path, chars_file, output_bin, size):
    # 加载字体
    font = ImageFont.truetype(ttf_path, size)

    with open(chars_file, "r", encoding="utf-8") as f:
        chars = f.read()

    # 使用 16 像素宽度存储，高度为 size
    # 每行 2 字节（16位），共 size 行
    bytes_per_char = 2 * size

    with open(output_bin, "wb") as f_out:
        for char in chars:
            # 创建 16 x size 的黑色画布（统一使用 16 像素宽度存储）
            img = Image.new("1", (16, size), 0)
            draw = ImageDraw.Draw(img)
            # 渲染字符
            draw.text((0, 0), char, font=font, fill=1)
            # 导出为 bytes (16 x size 占用 2 * size 字节)
            # 使用 'raw' MONO_HLSB 模式
            f_out.write(img.tobytes())

    total_bytes = len(chars) * bytes_per_char
    print(f"完成！生成 {output_bin}")
    print(f"字符数: {len(chars)}, 每字符 {bytes_per_char} 字节")
    print(f"总大小: {total_bytes / 1024:.2f} KB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成字体二进制文件")
    parser.add_argument("ttf_path", help="TrueType 字体文件路径")
    parser.add_argument("chars_file", help="包含字符的文本文件路径")
    parser.add_argument("output_bin", help="输出二进制文件路径")
    parser.add_argument("--size", type=int, default=16, help="字体大小/高度 (默认: 16)")

    args = parser.parse_args()

    generate_font_bin(args.ttf_path, args.chars_file, args.output_bin, args.size)
