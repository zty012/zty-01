"""
集成 UI 框架到现有项目的示例
演示如何在现有的 zty-01 项目中使用 UI 框架
"""

import time

import network
from machine import I2C, RTC, Pin

import ssd1306
from config import config
from led import set_led_color
from ntp import Ntp
from ui_framework.component import Circle, Label, Menu, ProgressBar, Text
from ui_framework.framework import UIFramework
from ui_framework.page import Page

# ============ 自定义页面 ============


class MainMenuPage(Page):
    """主菜单页面"""

    def __init__(self):
        super().__init__("MainMenu")

        # 菜单
        self.menu = Menu("Home", x=0, y=0, width=128)
        self.menu.add_item("System Info", lambda: self.goto("system_info"))
        self.menu.add_item("Clock", lambda: self.goto("clock"))
        self.menu.add_item("Network", lambda: self.goto("network"))
        self.menu.add_item("LED Control", lambda: self.goto("led_control"))
        self.menu.add_item("Button Test", lambda: self.goto("button_test"))
        self.add_component(self.menu)

    def goto(self, page_name):
        """跳转到指定页面"""
        if self.manager:
            self.manager.push_page(page_name)

    def _handle_page_event(self, event):
        """处理页面事件"""
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


class SystemInfoPage(Page):
    """系统信息页面"""

    def __init__(self):
        super().__init__("SystemInfo")

        # 标题
        title = Text("System Info", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # CPU 频率
        import os

        import machine

        cpu_freq = machine.freq() // 1_000_000
        self.add_component(Text(f"CPU: {cpu_freq}MHz", x=2, y=16))

        # 系统名称
        sys_name = os.uname().machine
        self.add_component(Text(f"MCU: {sys_name[:16]}", x=2, y=26))

        # 内存信息
        import gc

        gc.collect()
        free_mem = gc.mem_free() // 1024
        self.add_component(Text(f"Free: {free_mem}KB", x=2, y=36))

    def _handle_page_event(self, event):
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False


class ClockPage(Page):
    """时钟显示页面"""

    def __init__(self):
        super().__init__("Clock")

        # 标题
        self.title = Text("Clock", x=64, y=2)
        self.title.align = "center"
        self.add_component(self.title)

        # 时间显示（大字体效果，使用两行）
        self.time_label = Text("00:00:00", x=64, y=24)
        self.time_label.align = "center"
        self.add_component(self.time_label)

        # 日期显示
        self.date_label = Text("2024-01-01", x=64, y=36)
        self.date_label.align = "center"
        self.add_component(self.date_label)

        # 星期显示
        self.weekday_label = Text("Monday", x=64, y=48)
        self.weekday_label.align = "center"
        self.add_component(self.weekday_label)

        # 星期映射
        self.weekdays = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

    def update(self, delta_time):
        """更新时钟显示"""
        super().update(delta_time)

        if self.active:
            try:
                t = time.localtime()
                self.time_label.text = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])
                self.date_label.text = "{:04d}-{:02d}-{:02d}".format(t[0], t[1], t[2])
                # t[6] 是星期几 (0=Monday)
                if 0 <= t[6] < 7:
                    self.weekday_label.text = self.weekdays[t[6]]
            except Exception as e:
                self.time_label.text = "Time Error"
                print(f"Clock update error: {e}")

    def _handle_page_event(self, event):
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False


class NetworkPage(Page):
    """网络状态页面"""

    def __init__(self):
        super().__init__("Network")

        # 标题
        title = Text("Network", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # 状态
        self.status_label = Text("Status: --", x=2, y=16)
        self.add_component(self.status_label)

        # SSID
        self.ssid_label = Text("SSID: --", x=2, y=26)
        self.add_component(self.ssid_label)

        # IP 地址
        self.ip_label = Text("IP: --", x=2, y=36)
        self.add_component(self.ip_label)

    def on_enter(self):
        """页面进入时更新网络信息"""
        super().on_enter()
        self.update_network_info()

    def update_network_info(self):
        """更新网络信息"""
        try:
            sta_if = network.WLAN(network.STA_IF)
            if sta_if.isconnected():
                self.status_label.text = "Status: Connected"
                # 获取 SSID（如果可能）
                wifi_config = config.get("wifi", {})
                ssid = wifi_config.get("ssid", "Unknown")
                self.ssid_label.text = f"SSID: {ssid[:16]}"
                # 获取 IP
                ip = sta_if.ifconfig()[0]
                self.ip_label.text = f"IP: {ip}"
            else:
                self.status_label.text = "Status: Disconnected"
                self.ssid_label.text = "SSID: --"
                self.ip_label.text = "IP: --"
        except Exception as e:
            self.status_label.text = "Status: Error"
            print(f"Network info error: {e}")

    def _handle_page_event(self, event):
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False


class LEDControlPage(Page):
    """LED 控制页面"""

    def __init__(self):
        super().__init__("LEDControl")

        # 标题
        title = Text("LED Control", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # RGB 值标签
        self.r_label = Label("R: 0", x=10, y=16, width=108, height=12, border=True)
        self.add_component(self.r_label)

        self.g_label = Label("G: 0", x=10, y=30, width=108, height=12, border=True)
        self.add_component(self.g_label)

        self.b_label = Label("B: 0", x=10, y=44, width=108, height=12, border=True)
        self.add_component(self.b_label)

        # 当前选择的通道
        self.selected = 0  # 0=R, 1=G, 2=B
        self.labels = [self.r_label, self.g_label, self.b_label]

        # RGB 值
        self.r = 0
        self.g = 0
        self.b = 0

        self.update_display()

    def update_display(self):
        """更新显示"""
        self.r_label.text = f"R: {self.r}"
        self.g_label.text = f"G: {self.g}"
        self.b_label.text = f"B: {self.b}"

        # 高亮当前选中的标签
        for i, label in enumerate(self.labels):
            label.border = i == self.selected

    def apply_led(self):
        """应用 LED 颜色"""
        try:
            set_led_color(self.r, self.g, self.b)
        except Exception as e:
            print(f"LED control error: {e}")

    def _handle_page_event(self, event):
        if event.get("type") == "key_press":
            key = event.get("key")

            if key == "back":
                # 恢复 LED 关闭
                set_led_color(0, 0, 0)
                if self.manager:
                    self.manager.pop_page()
                return True

            elif key == "up":
                # 切换到上一个通道
                self.selected = (self.selected - 1) % 3
                self.update_display()
                return True

            elif key == "down":
                # 切换到下一个通道
                self.selected = (self.selected + 1) % 3
                self.update_display()
                return True

            elif key == "ok":
                # 增加当前通道的值
                if self.selected == 0:
                    self.r = (self.r + 5) % 256
                elif self.selected == 1:
                    self.g = (self.g + 5) % 256
                elif self.selected == 2:
                    self.b = (self.b + 5) % 256

                self.update_display()
                self.apply_led()
                return True

        return False


class ButtonTestPage(Page):
    """按钮测试页面"""

    def __init__(self):
        super().__init__("ButtonTest")

        # 标题
        title = Text("Button Test", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # 按钮状态显示
        self.k1_label = Text("K1: -", x=10, y=20)
        self.add_component(self.k1_label)

        self.k2_label = Text("K2: -", x=10, y=32)
        self.add_component(self.k2_label)

        self.k3_label = Text("K3: -", x=70, y=20)
        self.add_component(self.k3_label)

        self.k4_label = Text("K4: -", x=70, y=32)
        self.add_component(self.k4_label)

        # 事件计数器
        self.event_count = 0
        self.event_label = Text("Events: 0", x=10, y=46)
        self.add_component(self.event_label)

    def _handle_page_event(self, event):
        if event.get("type") in ["key_press", "key_release"]:
            # 更新事件计数
            self.event_count += 1
            self.event_label.text = f"Events: {self.event_count}"

            # 获取物理按键名
            physical_key = event.get("physical_key", event.get("key"))
            is_pressed = event.get("type") == "key_press"
            state = "ON" if is_pressed else "OFF"

            # 更新对应按钮的状态
            if physical_key == "k1":
                self.k1_label.text = f"K1: {state}"
            elif physical_key == "k2":
                self.k2_label.text = f"K2: {state}"
            elif physical_key == "k3":
                self.k3_label.text = f"K3: {state}"
            elif physical_key == "k4":
                self.k4_label.text = f"K4: {state}"

            # BACK 键退出
            if event.get("key") == "back" and is_pressed:
                if self.manager:
                    self.manager.pop_page()

            return True

        return False


# ============ 主程序 ============


def setup_ui():
    """初始化 UI 系统"""

    # 初始化 I2C 和显示器
    scl = Pin(16)
    sda = Pin(15)
    i2c = I2C(scl=scl, sda=sda)
    display = ssd1306.SSD1306_I2C(128, 64, i2c)

    # 创建 UI 框架
    ui = UIFramework(display)

    # 注册按钮（GPIO 引脚号根据您的硬件）
    ui.register_button("k1", 7)  # K1 -> GPIO 7
    ui.register_button("k2", 6)  # K2 -> GPIO 6
    ui.register_button("k3", 5)  # K3 -> GPIO 5
    ui.register_button("k4", 4)  # K4 -> GPIO 4

    # 设置按键映射
    ui.set_key_mapping("k1", "ok")  # K1 = 确认
    ui.set_key_mapping("k2", "back")  # K2 = 取消
    ui.set_key_mapping("k3", "up")  # K3 = 上
    ui.set_key_mapping("k4", "down")  # K4 = 下

    # 注册所有页面
    ui.register_page("main_menu", MainMenuPage())
    ui.register_page("system_info", SystemInfoPage())
    ui.register_page("clock", ClockPage())
    ui.register_page("network", NetworkPage())
    ui.register_page("led_control", LEDControlPage())
    ui.register_page("button_test", ButtonTestPage())

    # 跳转到主菜单
    ui.goto_page("main_menu", clear_stack=True)

    return ui


def main():
    """主函数"""
    print("\n" + "=" * 40)
    print("ZTY-01 UI Framework Demo")
    print("=" * 40 + "\n")

    # 初始化 LED（蓝色表示启动中）
    set_led_color(0, 0, 10)

    # 设置 UI
    ui = setup_ui()

    # LED 关闭表示就绪
    set_led_color(0, 0, 0)

    print("UI initialized and ready!")
    print("Controls: K1=OK, K2=Back, K3=Up, K4=Down")
    print("\nRunning main loop...\n")

    # 运行主循环
    try:
        ui.run()
    except KeyboardInterrupt:
        print("\n\nUI stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\nError in UI: {e}")
        import sys

        sys.print_exception(e)
        # LED 红色表示错误
        set_led_color(10, 0, 0)
    finally:
        # 清理：关闭 LED
        set_led_color(0, 0, 0)
        print("\nUI framework stopped.")


if __name__ == "__main__":
    main()
