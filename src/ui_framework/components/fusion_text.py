"""
Fusion 文本组件
"""

import framebuf

from ui_framework.components.base import Component


class FusionText(Component):
    """Fusion 文本组件，支持中英文混合显示（中文12x12，英文6x12）"""

    # 类级别的共享资源
    _fusion_index = None
    _fusion_file = None
    _fusion_cache = {}
    _initialized = False

    # 字体尺寸常量
    CHAR_HEIGHT = 12
    ASCII_WIDTH = 6
    CJK_WIDTH = 12
    # 每个字符的字节数：12行 * 2字节/行 = 24字节
    BYTES_PER_CHAR = 24

    @classmethod
    def init_fusion(cls, bin_path, chars_path):
        """
        初始化 Fusion 字体资源（全局调用一次）

        Args:
            bin_path: fusion.bin 文件路径
            chars_path: chars.txt 文件路径
        """
        if cls._initialized:
            return

        # 加载索引字符串到 RAM
        with open(chars_path, "r", encoding="utf-8") as f:
            cls._fusion_index = f.read()

        # 打开字体文件（保持打开状态）
        cls._fusion_file = open(bin_path, "rb")
        cls._initialized = True

    @classmethod
    def cleanup(cls):
        """清理资源"""
        if cls._fusion_file:
            cls._fusion_file.close()
            cls._fusion_file = None
        cls._fusion_index = None
        cls._fusion_cache.clear()
        cls._initialized = False

    def __init__(
        self, text="", x=0, y=0, color=1, max_width=None, auto_wrap=True, align="left"
    ):
        """
        初始化 Fusion 文本组件

        Args:
            text: 显示的文本
            x: x 坐标
            y: y 坐标
            color: 文本颜色 (0=黑, 1=白)
            max_width: 最大宽度（用于自动换行），None 表示 120
            auto_wrap: 是否自动换行
            align: 对齐方式 ("left", "center", "right")
        """
        super().__init__(x, y)
        self.text = text
        self.color = color
        self.max_width = max_width if max_width is not None else 120
        self.auto_wrap = auto_wrap
        self.align = align
        self.line_height = self.CHAR_HEIGHT

    def _get_char_data(self, char):
        """
        获取字符的位图数据

        Args:
            char: 字符

        Returns:
            bytes: 24 字节的位图数据（12行 * 2字节/行），如果字符不存在则返回 None
        """
        if not self.__class__._initialized:
            raise RuntimeError("FusionText 未初始化，请先调用 FusionText.init_fusion()")

        # 检查缓存
        if char in self.__class__._fusion_cache:
            return self.__class__._fusion_cache[char]

        try:
            # 检查资源是否可用
            if (
                self.__class__._fusion_index is None
                or self.__class__._fusion_file is None
            ):
                return None

            # 在索引中查找字符
            idx = self.__class__._fusion_index.find(char)
            if idx == -1:
                return None

            # 读取字体数据
            self.__class__._fusion_file.seek(idx * self.BYTES_PER_CHAR)
            data = self.__class__._fusion_file.read(self.BYTES_PER_CHAR)

            # 缓存字符（限制缓存大小）
            if len(self.__class__._fusion_cache) < 500:
                self.__class__._fusion_cache[char] = data

            return data
        except:
            return None

    def _render_self(self, display):
        """渲染文本"""
        if not self.text:
            return

        # 处理对齐方式
        start_x = self.x
        if self.align == "center":
            text_width = self.get_text_width()
            start_x = self.x - text_width // 2
        elif self.align == "right":
            text_width = self.get_text_width()
            start_x = self.x - text_width

        cursor_x = start_x
        cursor_y = self.y

        for char in self.text:
            # 换行处理
            if char == "\n":
                cursor_y += self.line_height
                cursor_x = start_x
                continue

            code = ord(char)
            is_ascii = code < 128

            # 获取位图
            bitmap = self._get_char_data(char)
            if not bitmap:
                # 如果字符不存在，跳过并移动光标
                cursor_x += self.ASCII_WIDTH if is_ascii else self.CJK_WIDTH
                continue

            # 渲染字符
            # 位图格式：16像素宽（2字节/行），12行高，使用 MONO_HLSB 格式
            fb = framebuf.FrameBuffer(
                bytearray(bitmap), 16, self.CHAR_HEIGHT, framebuf.MONO_HLSB
            )
            display.blit(fb, cursor_x, cursor_y)

            if is_ascii:
                # ASCII 字符：16x12 位图，但只占用 6 像素宽度
                cursor_x += self.ASCII_WIDTH
            else:
                # 中文字符：16x12 位图，占用 12 像素宽度
                cursor_x += self.CJK_WIDTH

            # 自动换行
            if self.auto_wrap and cursor_x > self.max_width:
                cursor_x = start_x
                cursor_y += self.line_height

    def get_text_width(self, text=None):
        """
        计算文本宽度

        Args:
            text: 要计算的文本，None 表示使用 self.text

        Returns:
            int: 文本宽度（像素）
        """
        if text is None:
            text = self.text

        width = 0
        for char in text:
            if char == "\n":
                continue
            code = ord(char)
            is_ascii = code < 128
            width += self.ASCII_WIDTH if is_ascii else self.CJK_WIDTH

        return width

    def get_text_height(self, text=None):
        """
        计算文本高度（考虑换行）

        Args:
            text: 要计算的文本，None 表示使用 self.text

        Returns:
            int: 文本高度（像素）
        """
        if text is None:
            text = self.text

        lines = 1
        cursor_x = 0

        for char in text:
            if char == "\n":
                lines += 1
                cursor_x = 0
                continue

            code = ord(char)
            is_ascii = code < 128
            char_width = self.ASCII_WIDTH if is_ascii else self.CJK_WIDTH

            # 检查是否需要自动换行
            if self.auto_wrap and cursor_x + char_width > self.max_width:
                lines += 1
                cursor_x = char_width
            else:
                cursor_x += char_width

        return lines * self.line_height
