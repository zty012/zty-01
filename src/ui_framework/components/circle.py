"""
圆形组件
"""

from ui_framework.components.base import Component


class Circle(Component):
    """圆形组件"""

    def __init__(self, x=0, y=0, radius=5, color=1, fill=False):
        """
        初始化圆形

        Args:
            x, y: 圆心坐标
            radius: 半径
            color: 颜色
            fill: 是否填充
        """
        super().__init__(x, y)
        self.radius = radius
        self.color = color
        self.fill = fill

    def _render_self(self, display):
        """渲染圆形"""
        display.ellipse(self.x, self.y, self.radius, self.radius, self.color, self.fill)
