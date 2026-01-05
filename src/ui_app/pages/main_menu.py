"""
主菜单页面
"""

from ui_framework.components.menu import Menu
from ui_framework.page import Page


class MainMenu(Page):
    """主菜单"""

    def __init__(self):
        super().__init__("MainMenu")

        # 菜单
        self.menu = Menu("Menu", x=0, y=0, width=128)
        self.menu.add_item("Whale", lambda: self.goto("whale"))
        self.menu.add_item("Snake Game", lambda: self.goto("snake_game"))
        self.menu.add_item("Flappy Bird", lambda: self.goto("flappy_bird"))
        self.menu.add_item("LED", lambda: self.goto("led"))
        self.menu.add_item("Settings", lambda: self.goto("settings"))
        self.add_component(self.menu)

    def goto(self, page_name):
        if self.manager:
            self.manager.push_page(page_name)

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
