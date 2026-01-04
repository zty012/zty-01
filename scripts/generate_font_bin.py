#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont


def generate_font_bin(ttf_path, chars_file, output_bin):
    # 加载字体，16像素
    font = ImageFont.truetype(ttf_path, 16)

    with open(chars_file, "r", encoding="utf-8") as f:
        chars = f.read()

    with open(output_bin, "wb") as f_out:
        for char in chars:
            # 创建 16x16 黑色画布
            img = Image.new("1", (16, 16), 0)
            draw = ImageDraw.Draw(img)
            # 渲染字符
            draw.text((0, 0), char, font=font, fill=1)
            # 导出为 bytes (16x16 占用 32 字节)
            # 使用 'raw' MONO_HLSB 模式
            f_out.write(img.tobytes())

    print(f"完成！生成 {output_bin}, 大小: {len(chars) * 32 / 1024:.2f} KB")


# 运行
generate_font_bin("unifont.ttf", "unifont_chars.txt", "unifont.bin")
