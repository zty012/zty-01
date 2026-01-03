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

    def __init__(self, display):
        """
        初始化 UI 框架

        Args:
            display: SSD1306 显示对象
        """
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


# ============ 示例页面 ============


class HomePage(Page):
    """主页示例"""

    def __init__(self):
        super().__init__("Home")

        # 菜单
        self.menu = Menu("Main Menu", x=0, y=0, width=128)
        self.menu.add_item("Clock", lambda: self.goto("clock"))
        self.menu.add_item("Settings", lambda: self.goto("settings"))
        self.menu.add_item("About", lambda: self.goto("about"))
        self.menu.add_item("Demo", lambda: self.goto("demo"))
        self.add_component(self.menu)

    def goto(self, page_name):
        """跳转到指定页面"""
        if self.manager:
            self.manager.push_page(page_name)

    def _handle_page_event(self, event):
        """处理页面级事件"""
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
        return False


class ClockPage(Page):
    """时钟页面示例"""

    def __init__(self):
        super().__init__("Clock")

        # 标题
        self.title = Text("Clock", x=64, y=2)
        self.title.align = "center"
        self.add_component(self.title)

        # 时间显示
        self.time_label = Text("00:00:00", x=64, y=28)
        self.time_label.align = "center"
        self.add_component(self.time_label)

        # 日期显示
        self.date_label = Text("2024-01-01", x=64, y=40)
        self.date_label.align = "center"
        self.add_component(self.date_label)

    def update(self, delta_time):
        """更新时钟显示"""
        super().update(delta_time)

        if self.active:
            try:
                import time

                # 获取当前时间
                t = time.localtime()
                self.time_label.text = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])
                self.date_label.text = "{:04d}-{:02d}-{:02d}".format(t[0], t[1], t[2])
            except Exception as e:
                self.time_label.text = "Time Error"
                print(f"Clock update error: {e}")

    def _handle_page_event(self, event):
        """处理返回事件"""
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False


class SettingsPage(Page):
    """设置页面示例"""

    def __init__(self):
        super().__init__("Settings")

        # 设置菜单
        self.menu = Menu("Settings", x=0, y=0, width=128)
        self.menu.add_item("Display", None)
        self.menu.add_item("Network", None)
        self.menu.add_item("System", None)
        self.menu.add_item("< Back", lambda: self.go_back())
        self.add_component(self.menu)

    def go_back(self):
        """返回上一页"""
        if self.manager:
            self.manager.pop_page()

    def _handle_page_event(self, event):
        """处理事件"""
        if event.get("type") == "key_press":
            key = event.get("key")
            if key == "back":
                self.go_back()
                return True
        return False


class AboutPage(Page):
    """关于页面示例"""

    def __init__(self):
        super().__init__("About")

        # 标题
        title = Text("About", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # 信息文本
        info1 = Text("UI Framework", x=64, y=20)
        info1.align = "center"
        self.add_component(info1)

        info2 = Text("v1.0.0", x=64, y=32)
        info2.align = "center"
        self.add_component(info2)

    def _handle_page_event(self, event):
        """处理返回事件"""
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False


class DemoPage(Page):
    """演示页面，展示各种组件"""

    def __init__(self):
        super().__init__("Demo")

        # 标题
        title = Text("Components", x=64, y=2)
        title.align = "center"
        self.add_component(title)

        # 进度条
        self.progress = ProgressBar(
            x=10, y=16, width=108, height=8, value=0, max_value=100
        )
        self.add_component(self.progress)

        # 按钮
        self.button = Button("Click", x=10, y=28, width=50, height=14)
        self.button.focused = True
        self.add_component(self.button)

        # 圆形动画
        self.circle = Circle(x=90, y=35, radius=6, fill=True)
        self.add_component(self.circle)

        # 动画状态
        self.anim_progress = 0

    def update(self, delta_time):
        """更新动画"""
        super().update(delta_time)

        if self.active:
            # 更新进度条
            self.anim_progress += delta_time * 20  # 每秒增加20
            if self.anim_progress > 100:
                self.anim_progress = 0
            self.progress.set_value(int(self.anim_progress))

            # 圆形左右移动
            self.circle.x = int(80 + 20 * abs((self.anim_progress % 100) / 50 - 1))

    def _handle_page_event(self, event):
        """处理事件"""
        if event.get("type") == "key_press":
            key = event.get("key")
            if key == "back":
                if self.manager:
                    self.manager.pop_page()
                return True
            elif key == "ok":
                print("Button clicked!")
                return True
        return False


def create_default_ui(display):
    """
    创建默认 UI 实例（快速开始用）

    Args:
        display: SSD1306 显示对象

    Returns:
        UIFramework: 配置好的 UI 框架实例
    """
    ui = UIFramework(display)

    # 注册示例页面
    ui.register_page("home", HomePage())
    ui.register_page("clock", ClockPage())
    ui.register_page("settings", SettingsPage())
    ui.register_page("about", AboutPage())
    ui.register_page("demo", DemoPage())

    # 设置默认页面
    ui.goto_page("home", clear_stack=True)

    return ui
