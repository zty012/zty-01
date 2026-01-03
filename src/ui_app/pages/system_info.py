"""
系统信息页面
"""

import os
import time

import machine

from ui_framework.components.text import Text
from ui_framework.page import Page


class SystemInfoPage(Page):
    """系统信息页面"""

    def __init__(self):
        super().__init__("SystemInfo")

        # 标题
        title = Text("System Info", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # 平台信息
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
