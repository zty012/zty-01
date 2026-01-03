"""
UI 框架主类
整合页面管理器、输入管理器和组件系统
"""

import time

from ui_framework.components.box import Box
from ui_framework.components.button import Button
from ui_framework.components.circle import Circle
from ui_framework.components.label import Label
from ui_framework.components.menu import Menu
from ui_framework.components.progress_bar import ProgressBar
from ui_framework.components.text import Text
from ui_framework.input import InputManager, KeyMapper
from ui_framework.page import Page, PageManager
from ui_framework.transitions import (
    FadeTransition,
    NoTransition,
    PushTransition,
    SlideTransition,
    WipeTransition,
)


class UIFramework:
    """UI 框架主类"""

    instance = None  # type: UIFramework | None

    def __init__(self, display):
        """
        初始化 UI 框架

        Args:
            display: SSD1306 显示对象
        """
        UIFramework.instance = self
        self.display = display
        self.page_manager = PageManager(display)
        self.input_manager = InputManager()
        self.key_mapper = KeyMapper()
        self.running = False
        self.fps = 30  # 目标帧率
        self.frame_time = 1.0 / self.fps
        self.last_update_time = 0

    def register_page(self, name, page):
        """
        注册页面

        Args:
            name: 页面名称
            page: 页面对象

        Returns:
            page: 返回注册的页面对象
        """
        return self.page_manager.register_page(name, page)

    def set_default_transition(self, transition):
        """
        设置默认页面过渡动画

        Args:
            transition: 过渡动画对象或字符串
                - Transition 对象：直接使用
                - 字符串：支持 "slide_left", "slide_right", "slide_up", "slide_down",
                         "fade", "wipe_left", "wipe_right", "push_left", "push_right", "none"
        """
        if isinstance(transition, str):
            transition = self._create_transition_from_string(transition)
        self.page_manager.set_default_transition(transition)

    def _create_transition_from_string(self, name, duration=0.3):
        """
        从字符串创建过渡动画对象

        Args:
            name: 动画名称
            duration: 动画持续时间
        """
        name_lower = name.lower()
        if name_lower == "slide_left":
            return SlideTransition(duration, "left")
        elif name_lower == "slide_right":
            return SlideTransition(duration, "right")
        elif name_lower == "slide_up":
            return SlideTransition(duration, "up")
        elif name_lower == "slide_down":
            return SlideTransition(duration, "down")
        elif name_lower == "fade":
            return FadeTransition(duration)
        elif name_lower == "wipe_left":
            return WipeTransition(duration, "left")
        elif name_lower == "wipe_right":
            return WipeTransition(duration, "right")
        elif name_lower == "wipe_up":
            return WipeTransition(duration, "up")
        elif name_lower == "wipe_down":
            return WipeTransition(duration, "down")
        elif name_lower == "push_left":
            return PushTransition(duration, "left")
        elif name_lower == "push_right":
            return PushTransition(duration, "right")
        elif name_lower == "push_up":
            return PushTransition(duration, "up")
        elif name_lower == "push_down":
            return PushTransition(duration, "down")
        elif name_lower == "none":
            return NoTransition()
        else:
            print(f"Warning: Unknown transition '{name}', using no transition")
            return NoTransition()

    def goto_page(self, name, clear_stack=False, transition=None):
        """
        切换到指定页面

        Args:
            name: 页面名称
            clear_stack: 是否清空页面栈
            transition: 过渡动画（None=使用默认，False=无动画，字符串或Transition对象）
        """
        if isinstance(transition, str):
            transition = self._create_transition_from_string(transition)
        return self.page_manager.goto_page(name, clear_stack, transition)

    def push_page(self, name, transition=None):
        """
        推入新页面

        Args:
            name: 页面名称
            transition: 过渡动画（None=使用默认，False=无动画，字符串或Transition对象）
        """
        if isinstance(transition, str):
            transition = self._create_transition_from_string(transition)
        return self.page_manager.push_page(name, transition)

    def pop_page(self, transition=None):
        """
        弹出当前页面

        Args:
            transition: 过渡动画（None=使用默认，False=无动画，字符串或Transition对象）
        """
        if isinstance(transition, str):
            transition = self._create_transition_from_string(transition)
        return self.page_manager.pop_page(transition)

    def register_button(self, name, pin_num, pull=None, inverted=True):
        """
        注册按钮

        Args:
            name: 按钮名称
            pin_num: GPIO 引脚号
            pull: 上拉/下拉模式
            inverted: 是否反转逻辑
        """
        from machine import Pin

        if pull is None:
            pull = Pin.PULL_UP
        self.input_manager.register_button(name, pin_num, pull, inverted)

    def set_key_mapping(self, physical_key, logical_key, context="default"):
        """
        设置按键映射

        Args:
            physical_key: 物理按键名称
            logical_key: 逻辑按键名称
            context: 上下文名称
        """
        self.key_mapper.set_mapping(physical_key, logical_key, context)

    def update(self):
        """更新框架状态"""
        current_time = time.ticks_ms() / 1000.0
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        # 更新输入状态
        self.input_manager.update()

        # 处理输入事件
        while self.input_manager.has_events():
            event = self.input_manager.poll_event()
            if event:
                # 翻译按键映射
                translated_event = self.key_mapper.translate_event(event)
                # 让页面管理器处理事件
                self.page_manager.handle_event(translated_event)

        # 更新页面
        self.page_manager.update(delta_time)

        return delta_time

    def render(self):
        """渲染当前帧"""
        self.page_manager.render()

    def run_once(self):
        """运行一次更新和渲染循环"""
        delta_time = self.update()
        self.render()
        return delta_time

    def run(self):
        """运行主循环（阻塞）"""
        self.running = True
        self.last_update_time = time.ticks_ms() / 1000.0

        while self.running:
            frame_start = time.ticks_ms() / 1000.0

            # 更新和渲染
            self.run_once()

            # 帧率控制
            frame_elapsed = time.ticks_ms() / 1000.0 - frame_start
            if frame_elapsed < self.frame_time:
                time.sleep(self.frame_time - frame_elapsed)

    def stop(self):
        """停止主循环"""
        self.running = False
