from machine import I2C, Pin

import ssd1306
from common import connect_to_saved_networks, sync_time
from led import set_led_color


def main():
    """主函数 - 启动系统和 UI"""

    # 初始化 I2C 和 OLED 显示屏
    scl = Pin(16)
    sda = Pin(15)
    i2c = I2C(scl=scl, sda=sda)
    display = ssd1306.SSD1306_I2C(128, 64, i2c)
    display.fill(0)
    display.text("Loading...", 0, 0)
    display.show()

    # 加载提示
    set_led_color(2, 5, 16)

    try:
        from ui_framework.components.fusion_text import FusionText
        from ui_framework.components.unifont_text import UnifontText

        display.text("Loading fonts", 0, 8)
        display.show()
        UnifontText.init_unifont(
            bin_path="/assets/unifont.bin", chars_path="/assets/chars.txt"
        )
        FusionText.init_fusion(
            bin_path="/assets/fusion.bin", chars_path="/assets/chars.txt"
        )
        display.text("Connecting Wi-Fi", 0, 16)
        display.show()
        connect_to_saved_networks()
        display.text("Syncing time", 0, 24)
        display.show()
        sync_time()
        set_led_color(0, 0, 0)
    except Exception as e:
        set_led_color(10, 0, 0)
        display.text(str(e), 0, 24)
        # 继续运行，不中断 UI

    from ui_app.pages import create_ui
    from ui_framework.framework import UIFramework

    # 创建 UI 框架
    ui = UIFramework(display)

    # 注册按钮
    ui.register_button("k1", 4)
    ui.register_button("k2", 5)
    ui.register_button("k3", 6)
    ui.register_button("k4", 7)

    # 设置按键映射
    ui.set_key_mapping("k1", "up")
    ui.set_key_mapping("k2", "down")
    ui.set_key_mapping("k3", "back")
    ui.set_key_mapping("k4", "ok")

    ui.set_default_transition("push_left")

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
