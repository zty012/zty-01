"""
进度条组件
"""

from ui_framework.components.base import Component


class ProgressBar(Component):
    """进度条组件"""

    def __init__(self, x=0, y=0, width=100, height=8, value=0, max_value=100):
        """
        初始化进度条

        Args:
            x, y: 左上角坐标
            width, height: 进度条尺寸
            value: 当前值
            max_value: 最大值
        """
        super().__init__(x, y, width, height)
        self.value = value
        self.max_value = max_value
        self.border = True

    def set_value(self, value):
        """设置进度值"""
        self.value = max(0, min(value, self.max_value))

    def _render_self(self, display):
        """渲染进度条"""
        # 绘制边框
        if self.border:
            display.rect(self.x, self.y, self.width, self.height, 1, False)

        # 计算填充宽度
        if self.max_value > 0:
            fill_width = int((self.value / self.max_value) * (self.width - 2))
            if fill_width > 0:
                display.fill_rect(
                    self.x + 1, self.y + 1, fill_width, self.height - 2, 1
                )
