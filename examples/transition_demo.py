"""
页面过渡动画示例
演示各种页面切换动画效果
"""

from machine import I2C, Pin

from ssd1306 import SSD1306_I2C
from ui_framework.components.button import Button
from ui_framework.components.label import Label
from ui_framework.components.text import Text
from ui_framework.framework import UIFramework
from ui_framework.page import Page
from ui_framework.transitions import (
    FadeTransition,
    PushTransition,
    SlideTransition,
    WipeTransition,
)


def main():
    # 初始化 I2C 和 OLED 显示
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    display = SSD1306_I2C(128, 64, i2c)

    # 创建 UI 框架
    ui = UIFramework(display)

    # 设置默认过渡动画（使用字符串方式）
    ui.set_default_transition("slide_left")

    # 创建主菜单页面
    main_menu = Page("MainMenu")
    main_menu.add_component(
        Label(0, 0, "Transition Demo", width=128, height=16, align="center")
    )
    main_menu.add_component(Text(10, 20, "Press buttons to see"))
    main_menu.add_component(Text(10, 30, "different transitions:"))
    main_menu.add_component(Text(10, 45, "1: Slide  2: Fade"))
    main_menu.add_component(Text(10, 55, "3: Wipe   4: Push"))

    # 创建演示页面 1 - 滑动效果
    slide_page = Page("SlidePage")
    slide_page.add_component(
        Label(0, 0, "Slide Transition", width=128, height=16, align="center")
    )
    slide_page.add_component(Text(10, 25, "Sliding animation"))
    slide_page.add_component(Text(10, 35, "Left/Right/Up/Down"))

    def on_slide_back(btn):
        # 使用相反方向的滑动动画返回
        ui.pop_page(transition="slide_right")

    back_btn1 = Button(10, 50, 108, 12, "Back")
    back_btn1.on_click = on_slide_back
    slide_page.add_component(back_btn1)

    # 创建演示页面 2 - 淡入淡出效果
    fade_page = Page("FadePage")
    fade_page.add_component(
        Label(0, 0, "Fade Transition", width=128, height=16, align="center")
    )
    fade_page.add_component(Text(10, 25, "Fading animation"))
    fade_page.add_component(Text(10, 35, "(simulated on OLED)"))

    def on_fade_back(btn):
        ui.pop_page(transition="fade")

    back_btn2 = Button(10, 50, 108, 12, "Back")
    back_btn2.on_click = on_fade_back
    fade_page.add_component(back_btn2)

    # 创建演示页面 3 - 擦除效果
    wipe_page = Page("WipePage")
    wipe_page.add_component(
        Label(0, 0, "Wipe Transition", width=128, height=16, align="center")
    )
    wipe_page.add_component(Text(10, 25, "Wiping animation"))
    wipe_page.add_component(Text(10, 35, "Like a curtain"))

    def on_wipe_back(btn):
        # 使用对象方式创建动画，可以自定义持续时间
        ui.pop_page(transition=WipeTransition(duration=0.4, direction="right"))

    back_btn3 = Button(10, 50, 108, 12, "Back")
    back_btn3.on_click = on_wipe_back
    wipe_page.add_component(back_btn3)

    # 创建演示页面 4 - 推入效果
    push_page = Page("PushPage")
    push_page.add_component(
        Label(0, 0, "Push Transition", width=128, height=16, align="center")
    )
    push_page.add_component(Text(10, 25, "Pushing animation"))
    push_page.add_component(Text(10, 35, "Pages move together"))

    def on_push_back(btn):
        ui.pop_page(transition="push_right")

    back_btn4 = Button(10, 50, 108, 12, "Back")
    back_btn4.on_click = on_push_back
    push_page.add_component(back_btn4)

    # 创建无动画演示页面
    no_anim_page = Page("NoAnimPage")
    no_anim_page.add_component(
        Label(0, 0, "No Transition", width=128, height=16, align="center")
    )
    no_anim_page.add_component(Text(10, 25, "Instant switch"))
    no_anim_page.add_component(Text(10, 35, "No animation"))

    def on_no_anim_back(btn):
        ui.pop_page(transition=False)  # False 表示禁用动画

    back_btn5 = Button(10, 50, 108, 12, "Back (instant)")
    back_btn5.on_click = on_no_anim_back
    no_anim_page.add_component(back_btn5)

    # 注册页面
    ui.register_page("main", main_menu)
    ui.register_page("slide", slide_page)
    ui.register_page("fade", fade_page)
    ui.register_page("wipe", wipe_page)
    ui.register_page("push", push_page)
    ui.register_page("no_anim", no_anim_page)

    # 注册按钮
    ui.register_button("btn1", 14, inverted=True)  # GPIO 14
    ui.register_button("btn2", 27, inverted=True)  # GPIO 27
    ui.register_button("btn3", 26, inverted=True)  # GPIO 26
    ui.register_button("btn4", 25, inverted=True)  # GPIO 25
    ui.register_button("btn5", 33, inverted=True)  # GPIO 33

    # 定义按钮事件处理
    def handle_menu_events(event):
        if event.type == "button_down":
            if event.key == "btn1":
                # 使用向左滑动进入
                ui.push_page("slide", transition="slide_left")
            elif event.key == "btn2":
                # 使用淡入淡出
                ui.push_page("fade", transition="fade")
            elif event.key == "btn3":
                # 使用擦除效果（自定义对象）
                ui.push_page("wipe", transition=WipeTransition(0.35, "left"))
            elif event.key == "btn4":
                # 使用推入效果
                ui.push_page("push", transition="push_left")
            elif event.key == "btn5":
                # 无动画
                ui.push_page("no_anim", transition=False)

    # 重写主菜单的事件处理
    main_menu._handle_page_event = lambda event: handle_menu_events(event) or False

    # 进入主菜单
    ui.goto_page("main", clear_stack=True)

    # 运行主循环
    print("Transition Demo Started!")
    print("Press buttons to see different transition effects")
    ui.run()


if __name__ == "__main__":
    main()
