"""
矩形框组件
"""

from ui_framework.components.base import Component


class Box(Component):
    """矩形框组件"""

    def __init__(self, x=0, y=0, width=10, height=10, color=1, fill=False):
        """
        初始化矩形框

        Args:
            x, y: 左上角坐标
            width, height: 宽度和高度
            color: 边框颜色
            fill: 是否填充
        """
        super().__init__(x, y, width, height)
        self.color = color
        self.fill = fill

    def _render_self(self, display):
        """渲染矩形框"""
        display.rect(self.x, self.y, self.width, self.height, self.color, self.fill)
