#!/usr/bin/env python3


def generate_char_list():
    chars = []

    # 1. 添加基础 ASCII 字符 (32-126)
    # 包括空格、标点、数字、大小写字母
    for i in range(32, 127):
        chars.append(chr(i))

    # 2. 遍历 GB2312 编码范围
    # GB2312 编码范围：高字节 0xA1-0xFE, 低字节 0xA1-0xFE
    for high in range(0xA1, 0xFF):
        for low in range(0xA1, 0xFF):
            try:
                # 尝试解码 GB2312
                char_bytes = bytes([high, low])
                char = char_bytes.decode("gb2312")
                chars.append(char)
            except UnicodeDecodeError:
                # 忽略未定义区域
                continue

    # 3. 写入文件，使用 UTF-8 编码存储
    with open("chars.txt", "w", encoding="utf-8") as f:
        f.write("".join(chars))

    print(f"成功生成 chars.txt，包含字符总数: {len(chars)}")


if __name__ == "__main__":
    generate_char_list()
