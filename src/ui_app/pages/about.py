"""
关于页面
"""

from ui_framework.components.menu import Menu
from ui_framework.components.text import Text
from ui_framework.page import Page


class AboutPage(Page):
    """关于页面"""

    def __init__(self):
        super().__init__("About")

        # 版本信息
        from __init__ import __author__ as author
        from __init__ import __homepage__ as homepage
        from __init__ import __version__ as version

        self.menu = Menu("About zty-01", x=0, y=0, width=128)
        self.menu.add_item("Version:")
        self.menu.add_item(f" {version}")
        self.menu.add_item("Author:")
        self.menu.add_item(f" {author}")
        self.menu.add_item("Homepage:")
        self.menu.add_item(f" {homepage}")
        self.add_component(self.menu)

    def _handle_page_event(self, event):
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False
