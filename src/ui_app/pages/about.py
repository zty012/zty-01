"""
关于页面
"""

from ui_framework.components.text import Text
from ui_framework.page import Page


class AboutPage(Page):
    """关于页面"""

    def __init__(self):
        super().__init__("About")

        # 标题
        title = Text("About", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # 版本信息
        from __init__ import __version__

        version = Text(f"v{__version__}", x=64, y=32)
        version.align = "center"
        self.add_component(version)

        # UI 框架版本
        ui_ver = Text("UI Framework v1.0", x=64, y=44)
        ui_ver.align = "center"
        self.add_component(ui_ver)

    def _handle_page_event(self, event):
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False
