"""
图标组件
"""

from ui_framework.components.base import Component


class Icon(Component):
    """图标组件（使用简单的像素图案）"""

    def __init__(self, x=0, y=0, icon_data=None):
        """
        初始化图标

        Args:
            x, y: 左上角坐标
            icon_data: 图标数据，格式为 {'width': w, 'height': h, 'data': [...]}
        """
        super().__init__(x, y)
        self.icon_data = icon_data or {"width": 8, "height": 8, "data": []}

    def _render_self(self, display):
        """渲染图标"""
        if not self.icon_data or not self.icon_data.get("data"):
            return

        width = self.icon_data["width"]
        height = self.icon_data["height"]
        data = self.icon_data["data"]

        for row in range(height):
            if row >= len(data):
                break
            row_data = data[row]
            for col in range(width):
                if col < len(row_data) and row_data[col]:
                    display.pixel(self.x + col, self.y + row, 1)
