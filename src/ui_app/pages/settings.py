"""
设置页面
"""

from ui_framework.components.menu import Menu
from ui_framework.page import Page


class SettingsPage(Page):
    """设置页面"""

    def __init__(self):
        super().__init__("Settings")

        # 设置菜单
        self.menu = Menu("Settings", x=0, y=0, width=128)
        self.menu.add_item("Display", lambda: print("Display settings"))
        self.menu.add_item("Network", lambda: print("Network settings"))
        self.menu.add_item("Time", lambda: print("Time settings"))
        self.menu.add_item("About", lambda: self.manager.push_page("about"))
        self.add_component(self.menu)

    def _handle_page_event(self, event):
        if event.get("type") == "key_press":
            key = event.get("key")
            if key == "up":
                self.menu.select_prev()
                return True
            elif key == "down":
                self.menu.select_next()
                return True
            elif key == "ok":
                return self.menu.activate_selected()
            elif key == "back":
                if self.manager:
                    self.manager.pop_page()
                return True
        return False
