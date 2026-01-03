import os
import time

import machine
import network
from machine import I2C, RTC, Pin

import ssd1306
from __init__ import __author__, __homepage__, __version__
from config import config
from led import set_led_color
from ntp import Ntp
from ui_app.pages import create_ui
from ui_framework.framework import UIFramework


def hello():
    print()
    print("| Hello from zty-01!")
    print(f"| Version: {__version__}")
    print(f"| Author: {__author__}")
    print(f"| Homepage: {__homepage__}")
    print(f"| Running on {os.uname().machine}")
    print(f"| CPU Frequency: {machine.freq() // 1_000_000} MHz")
    print()


def sync_time():
    hosts = config.get(
        "ntp_hosts", ["0.pool.ntp.org", "1.pool.ntp.org", "2.pool.ntp.org"]
    )

    print()
    print("| Syncing time with NTP servers:")
    for i, host in enumerate(hosts):
        print(f"| Server {i}: {host}")
    print()

    _rtc = RTC()
    Ntp.set_datetime_callback(_rtc.datetime)
    Ntp.set_hosts(("0.pool.ntp.org", "1.pool.ntp.org", "2.pool.ntp.org"))
    Ntp.set_ntp_timeout(1)
    Ntp.set_timezone(8, 0)
    Ntp.set_epoch(Ntp.EPOCH_1970)
    Ntp.rtc_sync()
    year, month, day, hours, minutes, seconds, *_ = Ntp.time()
    print(
        f":: Current time: {year:04}-{month:02}-{day:02} {hours:02}:{minutes:02}:{seconds:02}",
    )


def connect_wlan():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    wifi_config = config.get("wifi", {})
    if not ("ssid" in wifi_config and "password" in wifi_config):
        print(
            "You can configure WiFi settings in config.json, or use the `config` module to set it programmatically."
        )
        return

    ssid = wifi_config["ssid"]
    password = wifi_config["password"]

    print(f":: Connecting to WiFi: {ssid}")
    sta_if.connect(ssid, password)
    # 等待连接成功或超时
    for _ in range(20):
        if sta_if.isconnected():
            break
        time.sleep(1)
    if sta_if.isconnected():
        print(f":: Successfully connected to: {ssid}")
        ip, subnet, gateway, dns = sta_if.ifconfig()
        print()
        print(f"| IP Address: {ip}")
        print(f"| Subnet Mask: {subnet}")
        print(f"| Gateway: {gateway}")
        print(f"| DNS: {dns}")
        print()
        sync_time()


def main():
    """主函数 - 启动系统和 UI"""

    # 打印欢迎信息
    hello()

    # LED 蓝色表示启动中
    set_led_color(2, 5, 16)

    # 连接 WiFi 和同步时间
    try:
        connect_wlan()
        set_led_color(0, 0, 0)
    except Exception as e:
        set_led_color(10, 0, 0)
        print(f"WiFi/NTP error: {e}")
        # 继续运行，不中断 UI

    # 初始化硬件
    print()
    print("=" * 40)
    print("Initializing UI System...")
    print("=" * 40)

    scl = Pin(16)
    sda = Pin(15)
    i2c = I2C(scl=scl, sda=sda)
    display = ssd1306.SSD1306_I2C(128, 64, i2c)

    # 创建 UI 框架
    print("Creating UI framework...")
    ui = UIFramework(display)

    # 注册按钮
    # K1: 确认
    # K2: 取消
    # K3: 上
    # K4: 下
    print("Registering buttons...")
    ui.register_button("k1", 7)
    ui.register_button("k2", 6)
    ui.register_button("k3", 5)
    ui.register_button("k4", 4)

    # 设置按键映射
    ui.set_key_mapping("k1", "ok")  # K1 = 确认
    ui.set_key_mapping("k2", "back")  # K2 = 取消
    ui.set_key_mapping("k3", "down")  # K3 = 下
    ui.set_key_mapping("k4", "up")  # K4 = 上

    # 创建实用页面
    print("Loading pages...")
    create_ui(ui)

    # 设置帧率
    ui.fps = 30

    # 准备就绪，关闭 LED
    set_led_color(0, 0, 0)

    print()
    print("UI Ready!")
    print("Controls:")
    print("  K1 = OK/Confirm")
    print("  K2 = Back/Cancel")
    print("  K3 = Up/Previous")
    print("  K4 = Down/Next")
    print()
    print("Starting main loop...")
    print()

    # 运行主循环
    try:
        ui.run()
    except KeyboardInterrupt:
        print("\n\nUI stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\nError in UI: {e}")
        import sys

        sys.print_exception(e)
        # 显示错误（红色 LED）
        set_led_color(10, 0, 0)
    finally:
        # 清理：关闭 LED
        set_led_color(0, 0, 0)
        print("UI system stopped.")


# 启动主程序
if __name__ == "__main__":
    main()
