import time

import network
from machine import RTC

from config import settings
from ntp import Ntp


def sync_time():
    hosts = settings.get(
        "ntp_hosts",
        [
            "ntp.aliyun.com",
            "cn.pool.ntp.org",
            "ntp.tuna.tsinghua.edu.cn",
            "0.pool.ntp.org",
            "1.pool.ntp.org",
            "2.pool.ntp.org",
        ],
    )

    _rtc = RTC()
    Ntp.set_datetime_callback(_rtc.datetime)
    Ntp.set_hosts(tuple(hosts))
    Ntp.set_ntp_timeout(1)
    Ntp.set_timezone(8, 0)
    Ntp.set_epoch(Ntp.EPOCH_1970)
    Ntp.rtc_sync()


def connect_to_saved_networks():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    saved_networks = settings.get("saved_networks", {})
    networks = sta_if.scan()
    # 按照信号强度排序，优先连接信号强的网络
    networks.sort(key=lambda x: x[3], reverse=True)
    for ssid, bssid, channel, rssi, security, hidden in networks:
        ssid_str = ssid.decode("utf-8")
        if ssid_str in saved_networks:
            password = saved_networks[ssid_str]
            sta_if.connect(ssid_str, password)
            # 等待连接结果
            for _ in range(10):
                if sta_if.isconnected():
                    print(f"Connected to {ssid_str}")
                    return True
                time.sleep(1)
            raise Exception(f"X {ssid_str}")
