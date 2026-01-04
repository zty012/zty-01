"""
文本组件
"""

from ui_framework.components.base import Component


class Text(Component):
    """文本组件"""

    def __init__(self, text="", x=0, y=0, color=1, align="left"):
        """
        初始化文本组件

        Args:
            text: 显示的文本
            x: x 坐标
            y: y 坐标
            color: 文本颜色 (0=黑, 1=白)
        """
        super().__init__(x, y)
        self.text = text
        self.color = color
        self.align = align

    def _render_self(self, display):
        """渲染文本"""
        if not self.text:
            return

        x = self.x
        if self.align == "center":
            text_width = len(self.text) * 8
            x = self.x - text_width // 2
        elif self.align == "right":
            text_width = len(self.text) * 8
            x = self.x - text_width

        display.text(self.text, x, self.y, self.color)
