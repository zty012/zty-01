"""
网络状态页面
"""

import network

from config import config
from ui_framework.components.text import Text
from ui_framework.page import Page


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
