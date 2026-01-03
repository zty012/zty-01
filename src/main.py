from machine import I2C, Pin

import ssd1306
from common import connect_to_saved_networks
from led import set_led_color
from ui_app.pages import create_ui
from ui_framework.framework import UIFramework


def main():
    """主函数 - 启动系统和 UI"""

    # 初始化 I2C 和 OLED 显示屏
    scl = Pin(16)
    sda = Pin(15)
    i2c = I2C(scl=scl, sda=sda)
    display = ssd1306.SSD1306_I2C(128, 64, i2c)

    # 加载提示
    set_led_color(2, 5, 16)

    # 连接 WiFi 和同步时间
    try:
        connect_to_saved_networks()
        set_led_color(0, 0, 0)
    except Exception as e:
        set_led_color(10, 0, 0)
        print(f"WiFi/NTP error: {e}")
        # 继续运行，不中断 UI

    # 创建 UI 框架
    ui = UIFramework(display)

    # 注册按钮
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
    create_ui(ui)

    # 设置帧率
    ui.fps = 60

    # 准备就绪，关闭 LED
    set_led_color(0, 0, 0)

    # 运行主循环
    try:
        ui.run()
    except KeyboardInterrupt:
        print("\n\nUI stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\nError in UI: {e}")
    finally:
        # 清理：关闭 LED
        set_led_color(0, 0, 0)
        print("UI system stopped.")
        # 显示错误（红色 LED）
        set_led_color(10, 0, 0)


# 启动主程序
if __name__ == "__main__":
    main()
