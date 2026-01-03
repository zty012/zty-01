"""
LED 测试页面
"""

import time

from led import set_led_color
from ui_framework.components.menu import Menu
from ui_framework.framework import UIFramework
from ui_framework.page import Page


class LEDPage(Page):
    """LED 页面"""

    def __init__(self):
        super().__init__("LEDTest")

        # 设置菜单
        self.menu = Menu("LED", x=0, y=0, width=128)
        self.menu.add_item("Flashbang", self.flashbang)
        self.menu.add_item("Strobe", self.strobe)
        self.menu.add_item("Fast strobe", self.fast_strobe)
        self.menu.add_item("Police", self.police)
        self.add_component(self.menu)

    def flashbang(self):
        set_led_color(255, 255, 255, 0)
        time.sleep(0.02)
        set_led_color(0, 0, 0, 0)

    def strobe(self):
        while not self._back_pressed():
            set_led_color(255, 255, 255, 0)
            time.sleep(0.1)
            set_led_color(0, 0, 0, 0)
            time.sleep(0.1)

    def fast_strobe(self):
        while not self._back_pressed():
            set_led_color(255, 255, 255, 0)
            time.sleep(0.05)
            set_led_color(0, 0, 0, 0)
            time.sleep(0.05)

    def police(self):
        while not self._back_pressed():
            set_led_color(255, 0, 0, 0)
            time.sleep(0.25)
            set_led_color(0, 0, 255, 0)
            time.sleep(0.25)

    def _back_pressed(self):
        return (
            UIFramework.instance.input_manager.buttons["k2"]["pin"].value() == 0
            if UIFramework.instance
            else False
        )

    def on_exit(self):
        """页面退出时关闭 LED"""
        set_led_color(0, 0, 0, 0)

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
