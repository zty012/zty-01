import time
import machine
from mylib.bh1750 import BH1750
from machine import I2C, RTC, Pin
import network
from mylib.ntp import Ntp
from config import config
from __init__ import __version__, __author__, __homepage__
import os
from led import set_led_color


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


set_led_color(2, 5, 16)
hello()
connect_wlan()
set_led_color(0, 0, 0)


i2c0_sda = Pin(18, mode=Pin.IN, pull=Pin.PULL_UP)
i2c0_scl = Pin(19, mode=Pin.IN, pull=Pin.PULL_UP)
i2c0 = I2C(0, sda=i2c0_sda, scl=i2c0_scl)

bh1750 = BH1750(0x23, i2c0)

while True:
    print(bh1750.measurement)
    time.sleep(1)
