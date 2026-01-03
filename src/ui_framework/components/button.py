"""
按钮组件
"""

from ui_framework.components.base import Component


class Button(Component):
    """按钮组件"""

    def __init__(self, text="Button", x=0, y=0, width=60, height=16, action=None):
        """
        初始化按钮

        Args:
            text: 按钮文本
            x, y: 左上角坐标
            width, height: 按钮尺寸
            action: 点击回调函数
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.action = action
        self.pressed = False

    def press(self):
        """按下按钮"""
        self.pressed = True
        if self.action:
            self.action()

    def release(self):
        """释放按钮"""
        self.pressed = False

    def _render_self(self, display):
        """渲染按钮"""
        # 绘制边框和背景
        if self.pressed or self.focused:
            display.fill_rect(self.x, self.y, self.width, self.height, 1)
            text_color = 0
        else:
            display.rect(self.x, self.y, self.width, self.height, 1, False)
            text_color = 1

        # 居中绘制文本
        text_width = len(self.text) * 8
        text_x = self.x + (self.width - text_width) // 2
        text_y = self.y + (self.height - 8) // 2
        display.text(self.text, text_x, text_y, text_color)

    def _handle_self_event(self, event):
        """处理按钮事件"""
        if event.get("type") == "key_press" and event.get("key") == "ok":
            if self.focused:
                self.press()
                return True
        elif event.get("type") == "key_release" and event.get("key") == "ok":
            if self.focused:
                self.release()
                return True
        return False
