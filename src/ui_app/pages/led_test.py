"""
LED 测试页面
"""

from led import set_led_color
from ui_framework.components.text import Text
from ui_framework.page import Page


class LEDTestPage(Page):
    """LED 测试页面"""

    def __init__(self):
        super().__init__("LEDTest")

        # 标题
        title = Text("LED Test", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # 当前颜色显示
        self.color_name_label = Text("Color: Off", x=64, y=18)
        self.color_name_label.align = "center"
        self.add_component(self.color_name_label)

        # RGB 值显示
        self.rgb_label = Text("RGB: 0,0,0", x=64, y=30)
        self.rgb_label.align = "center"
        self.add_component(self.rgb_label)

        # 颜色列表和当前索引
        self.colors = [
            {"name": "Off", "r": 0, "g": 0, "b": 0},
            {"name": "Red", "r": 16, "g": 0, "b": 0},
            {"name": "Green", "r": 0, "g": 16, "b": 0},
            {"name": "Blue", "r": 0, "g": 0, "b": 16},
            {"name": "Yellow", "r": 16, "g": 16, "b": 0},
            {"name": "Cyan", "r": 0, "g": 16, "b": 16},
            {"name": "Magenta", "r": 16, "g": 0, "b": 16},
            {"name": "White", "r": 8, "g": 8, "b": 8},
        ]
        self.color_index = 0

        # 指示器
        self.indicator_text = Text("< K3/K4: Change >", x=64, y=46)
        self.indicator_text.align = "center"
        self.add_component(self.indicator_text)

    def set_color(self, index):
        """设置 LED 颜色"""
        if 0 <= index < len(self.colors):
            color = self.colors[index]
            self.color_index = index

            # 更新显示
            self.color_name_label.text = f"Color: {color['name']}"
            self.rgb_label.text = f"RGB: {color['r']},{color['g']},{color['b']}"

            # 设置 LED
            try:
                set_led_color(color["r"], color["g"], color["b"])
            except Exception as e:
                print(f"LED control error: {e}")

    def on_enter(self):
        super().on_enter()
        self.set_color(self.color_index)

    def on_exit(self):
        super().on_exit()
        # 退出时关闭 LED
        try:
            set_led_color(0, 0, 0)
        except:
            pass

    def _handle_page_event(self, event):
        if event.get("type") == "key_press":
            key = event.get("key")

            if key == "back":
                if self.manager:
                    self.manager.pop_page()
                return True

            elif key == "up":
                # 上一个颜色
                new_index = (self.color_index - 1) % len(self.colors)
                self.set_color(new_index)
                return True

            elif key == "down":
                # 下一个颜色
                new_index = (self.color_index + 1) % len(self.colors)
                self.set_color(new_index)
                return True

        return False
