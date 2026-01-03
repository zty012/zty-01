"""
时钟页面
"""

import time

from ui_framework.components.text import Text
from ui_framework.page import Page


class ClockPage(Page):
    """实用时钟页面"""

    def __init__(self):
        super().__init__("Clock")

        # 时间显示（大号）
        self.time_label = Text("--:--:--", x=64, y=22)
        self.time_label.align = "center"
        self.add_component(self.time_label)

        # 日期显示
        self.date_label = Text("----/--/--", x=64, y=34)
        self.date_label.align = "center"
        self.add_component(self.date_label)

        # 星期显示
        self.weekday_label = Text("---", x=64, y=46)
        self.weekday_label.align = "center"
        self.add_component(self.weekday_label)

        # 顶部装饰线
        self.add_component(Text("=" * 16, x=0, y=2))

        # 底部装饰线
        self.add_component(Text("=" * 16, x=0, y=58))

        self.weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def update(self, delta_time):
        super().update(delta_time)
        if self.active:
            try:
                t = time.localtime()
                self.time_label.text = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])
                self.date_label.text = "{:04d}/{:02d}/{:02d}".format(t[0], t[1], t[2])
                if 0 <= t[6] < 7:
                    self.weekday_label.text = self.weekdays[t[6]]
            except Exception as e:
                self.time_label.text = "Error"
                print(f"Clock error: {e}")

    def _handle_page_event(self, event):
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False
