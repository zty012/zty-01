"""
时钟页面
"""

import time

from ntp import Ntp
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
                year, month, day, hour, minute, second, weekday, yearday, us = (
                    Ntp.time()
                )
                self.time_label.text = f"{hour:02}:{minute:02}:{second:02}"
                self.date_label.text = f"{year:04}/{month:02}/{day:02}"
                self.weekday_label.text = self.weekdays[weekday - 1]
            except Exception as e:
                self.time_label.text = "Error"
                print(f"Clock error: {e}")

    def _handle_page_event(self, event):
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False
