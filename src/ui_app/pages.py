"""
实用功能页面示例
包含：主菜单、时钟、系统信息、光传感器、网络状态等实用页面
"""

import time

import network
from machine import I2C, Pin

from config import config
from led import set_led_color
from ui_framework.component import Circle, Label, Menu, ProgressBar, Text
from ui_framework.page import Page


class MainMenu(Page):
    """实用主菜单"""

    def __init__(self):
        super().__init__("MainMenu")

        # 菜单
        self.menu = Menu("ZTY-01", x=0, y=0, width=128)
        self.menu.add_item("Clock", lambda: self.goto("clock"))
        self.menu.add_item("Network", lambda: self.goto("network"))
        self.menu.add_item("System Info", lambda: self.goto("system"))
        self.menu.add_item("LED Test", lambda: self.goto("led_test"))
        self.menu.add_item("About", lambda: self.goto("about"))
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
        return False


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


class NetworkStatusPage(Page):
    """网络状态页面"""

    def __init__(self):
        super().__init__("Network")

        # 标题
        title = Text("Network Status", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # 连接状态
        self.status_text = Text("Status: ---", x=2, y=16)
        self.add_component(self.status_text)

        # SSID
        self.ssid_text = Text("SSID: ---", x=2, y=26)
        self.add_component(self.ssid_text)

        # IP 地址
        self.ip_text = Text("IP: ---", x=2, y=36)
        self.add_component(self.ip_text)

        # 信号强度（如果可用）
        self.signal_text = Text("Signal: ---", x=2, y=46)
        self.add_component(self.signal_text)

        # 更新间隔
        self.update_timer = 0
        self.update_interval = 2.0  # 2 秒更新一次

    def update(self, delta_time):
        super().update(delta_time)
        if not self.active:
            return

        self.update_timer += delta_time
        if self.update_timer >= self.update_interval:
            self.update_timer = 0
            self.refresh_network_info()

    def refresh_network_info(self):
        """刷新网络信息"""
        try:
            sta_if = network.WLAN(network.STA_IF)

            if sta_if.isconnected():
                self.status_text.text = "Status: Connected"

                # 获取 SSID
                wifi_config = config.get("wifi", {})
                ssid = wifi_config.get("ssid", "Unknown")
                # 限制长度
                if len(ssid) > 14:
                    ssid = ssid[:13] + "."
                self.ssid_text.text = f"SSID: {ssid}"

                # 获取 IP
                ip = sta_if.ifconfig()[0]
                self.ip_text.text = f"IP: {ip}"

                # 尝试获取信号强度（部分平台支持）
                try:
                    # RSSI 信号强度（dBm）
                    # 注意：不是所有 MicroPython 版本都支持
                    rssi = sta_if.status("rssi")
                    self.signal_text.text = f"Signal: {rssi} dBm"
                except:
                    self.signal_text.text = "Signal: N/A"
            else:
                self.status_text.text = "Status: Disconnected"
                self.ssid_text.text = "SSID: ---"
                self.ip_text.text = "IP: ---"
                self.signal_text.text = "Signal: ---"

        except Exception as e:
            self.status_text.text = "Status: Error"
            print(f"Network info error: {e}")

    def on_enter(self):
        super().on_enter()
        self.update_timer = 0
        self.refresh_network_info()

    def _handle_page_event(self, event):
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False


class SystemInfoPage(Page):
    """系统信息页面"""

    def __init__(self):
        super().__init__("SystemInfo")

        # 标题
        title = Text("System Info", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # 平台信息
        import os

        import machine

        machine_name = os.uname().machine
        if len(machine_name) > 20:
            machine_name = machine_name[:19] + "."

        self.add_component(Text(f"MCU: {machine_name}", x=2, y=16))

        # CPU 频率
        cpu_freq = machine.freq() // 1_000_000
        self.add_component(Text(f"CPU: {cpu_freq} MHz", x=2, y=26))

        # 内存信息（动态更新）
        self.mem_text = Text("RAM: --- KB", x=2, y=36)
        self.add_component(self.mem_text)

        # 运行时间
        self.uptime_text = Text("Uptime: ---", x=2, y=46)
        self.add_component(self.uptime_text)

        # 启动时间记录
        self.start_time = time.ticks_ms()

    def update(self, delta_time):
        super().update(delta_time)
        if self.active:
            # 更新内存信息
            import gc

            gc.collect()
            free_mem = gc.mem_free() // 1024
            self.mem_text.text = f"RAM: {free_mem} KB"

            # 更新运行时间
            uptime_ms = time.ticks_diff(time.ticks_ms(), self.start_time)
            uptime_sec = uptime_ms // 1000
            hours = uptime_sec // 3600
            minutes = (uptime_sec % 3600) // 60
            seconds = uptime_sec % 60
            self.uptime_text.text = f"Up: {hours:02d}:{minutes:02d}:{seconds:02d}"

    def _handle_page_event(self, event):
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False


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


def create_ui(ui_framework):
    """
    创建实用 UI 页面

    Args:
        ui_framework: UIFramework 实例
    """
    # 注册所有实用页面
    ui_framework.register_page("main_menu", MainMenu())
    ui_framework.register_page("clock", ClockPage())
    ui_framework.register_page("network", NetworkStatusPage())
    ui_framework.register_page("system", SystemInfoPage())
    ui_framework.register_page("led_test", LEDTestPage())
    ui_framework.register_page("about", AboutPage())
    ui_framework.register_page("settings", SettingsPage())

    # 设置主菜单为首页
    ui_framework.goto_page("main_menu", clear_stack=True)
