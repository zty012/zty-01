"""
网络状态页面
"""

import time

import machine
import network

from common import sync_time
from config import save_settings, settings
from ui_app.pages.keyboard import KeyboardPage
from ui_framework.components.menu import Menu
from ui_framework.page import Page

statuses = {
    network.STAT_HANDSHAKE_TIMEOUT: "Handshake Timeout",
    network.STAT_NO_AP_FOUND_IN_RSSI_THRESHOLD: "Signal Too Weak",
    network.STAT_NO_AP_FOUND: "AP Not Found",
    network.STAT_NO_AP_FOUND_IN_AUTHMODE_THRESHOLD: "Auth Mode Mismatch",
    network.STAT_ASSOC_FAIL: "Association Failed",
    network.STAT_GOT_IP: "Connected",
    network.STAT_WRONG_PASSWORD: "Wrong Password",
    network.STAT_CONNECT_FAIL: "Connection Failed",
    network.STAT_BEACON_TIMEOUT: "Beacon Timeout",
    network.STAT_CONNECTING: "Connecting",
    network.STAT_NO_AP_FOUND_W_COMPATIBLE_SECURITY: "No Compatible AP",
    network.STAT_IDLE: "Idle",
}


class NetworkPage(Page):
    """网络配置页面"""

    def __init__(self):
        super().__init__("Network")

        self.temp_password_store = {}

        self.sta_if = network.WLAN(network.STA_IF)
        # 设置菜单
        self.menu = Menu("Network", x=0, y=0, width=128)
        self.add_component(self.menu)
        self.update_menu()

    def update_menu(self):
        self.menu.items = []
        self.menu.add_item("Refresh", self.update_menu)
        self.menu.add_item(statuses.get(self.sta_if.status(), "Unknown"))
        # print(self.sta_if.status())
        if self.sta_if.status() == network.STAT_GOT_IP:
            ssid = self.sta_if.config("essid")
            self.menu.add_item(ssid)
            self.menu.add_item("Disconnect", self.sta_if.disconnect)
            if ssid in settings.get("saved_networks", {}):
                self.menu.add_item("Forget", lambda: self.forget_network(ssid))
            else:
                self.menu.add_item(
                    "Save",
                    lambda: self.save_network(
                        ssid, self.temp_password_store.get(ssid, "")
                    ),
                )
            self.menu.add_item("-" * 16)
            ip, subnet, gateway, dns = self.sta_if.ifconfig()
            self.menu.add_item("IP:")
            self.menu.add_item(f" {ip}")
            self.menu.add_item("Gateway:")
            self.menu.add_item(f" {gateway}")
            self.menu.add_item("DNS:")
            self.menu.add_item(f" {dns}")
            self.menu.add_item("Signal Strength:")
            rssi = self.sta_if.status("rssi")
            self.menu.add_item(f" {rssi} dBm")
            sync_time()
        elif self.sta_if.status() == network.STAT_IDLE:
            self.menu.add_item("-" * 16)
            # scan
            networks = self.sta_if.scan()
            for ssid, bssid, channel, rssi, security, hidden in networks:
                if ssid == b"":
                    continue
                elif security == 0:
                    self.menu.add_item(
                        "[Open] " + ssid.decode("utf-8"),
                        lambda ssid=ssid.decode("utf-8"): self.connect_to_open_network(
                            ssid
                        ),
                    )
                elif ssid.decode("utf-8") in settings.get("saved_networks", {}):
                    saved_password = settings["saved_networks"][ssid.decode("utf-8")]
                    self.menu.add_item(
                        "[Saved] " + ssid.decode("utf-8"),
                        lambda ssid=ssid.decode("utf-8"),
                        pwd=saved_password: self.connect_to_network(ssid, pwd),
                    )
                else:
                    self.menu.add_item(
                        ssid.decode("utf-8"),
                        lambda ssid=ssid.decode("utf-8"): self.request_network_password(
                            ssid
                        ),
                    )
        self.menu.add_item("-" * 16)
        self.menu.add_item("Reset saved networks", self.reset_network)

    def reset_network(self):
        settings["saved_networks"] = {}
        save_settings()
        machine.reset()

    def connect_to_open_network(self, ssid):
        self.sta_if.connect(ssid)
        self.update_menu()

    def request_network_password(self, ssid):
        if self.manager:
            self.manager.push_page(
                KeyboardPage(
                    f"Pwd for {ssid}",
                    callback=lambda pwd: self.connect_to_network(ssid, pwd),
                )
            )

    def connect_to_network(self, ssid, password):
        if not password:
            return
        self.sta_if.connect(ssid, password)
        self.temp_password_store[ssid] = password
        self.update_menu()

    def forget_network(self, ssid):
        self.sta_if.disconnect()
        saved_networks = settings.get("saved_networks", {})
        if ssid in saved_networks:
            del saved_networks[ssid]
            save_settings()
        self.update_menu()

    def save_network(self, ssid, password):
        if "saved_networks" not in settings:
            settings["saved_networks"] = {}
        settings["saved_networks"][ssid] = password
        save_settings()

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
