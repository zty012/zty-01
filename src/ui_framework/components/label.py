"""
标签组件
"""

from ui_framework.components.base import Component


class Label(Component):
    """标签组件（带边框的文本）"""

    def __init__(self, text="", x=0, y=0, width=60, height=16, border=True):
        """
        初始化标签

        Args:
            text: 标签文本
            x, y: 左上角坐标
            width, height: 标签尺寸
            border: 是否显示边框
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.border = border
        self.align = "left"  # left, center, right

    def _render_self(self, display):
        """渲染标签"""
        if self.border:
            display.rect(self.x, self.y, self.width, self.height, 1, False)

        # 绘制文本
        text_x = self.x + 2
        text_y = self.y + (self.height - 8) // 2

        if self.align == "center":
            text_width = len(self.text) * 8
            text_x = self.x + (self.width - text_width) // 2
        elif self.align == "right":
            text_width = len(self.text) * 8
            text_x = self.x + self.width - text_width - 2

        display.text(self.text, text_x, text_y, 1)
