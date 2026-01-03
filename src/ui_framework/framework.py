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

    def goto_page(self, name, clear_stack=False):
        """
        切换到指定页面

        Args:
            name: 页面名称
            clear_stack: 是否清空页面栈
        """
        return self.page_manager.goto_page(name, clear_stack)

    def push_page(self, name):
        """推入新页面"""
        return self.page_manager.push_page(name)

    def pop_page(self):
        """弹出当前页面"""
        return self.page_manager.pop_page()

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
