"""
主菜单页面
"""

from ntp import Ntp
from ui_framework.components.text import Text
from ui_framework.components.unifont_text import UnifontText
from ui_framework.page import Page


class Home(Page):
    """首页"""

    def __init__(self):
        super().__init__("Home")

        self.el_time = UnifontText("--:--:--", 8, 8)
        self.add_component(self.el_time)

        self.el_date = Text("----/--/--", 8, 32)
        self.add_component(self.el_date)

    def update(self, delta_time):
        super().update(delta_time)
        year, month, day, hour, minute, second, weekday, yearday, us = Ntp.time()
        self.el_time.text = f"{hour:02}:{minute:02}:{second:02}"
        self.el_date.text = f"{year:04}/{month:02}/{day:02}"

    def _handle_page_event(self, event):
        if event.get("type") == "key_press":
            key = event.get("key")
            if key == "ok":
                if self.manager:
                    self.manager.push_page("main_menu")
                    return True
            elif key == "back":
                if self.manager:
                    self.manager.push_page("lessons")
                    return True
        return False
