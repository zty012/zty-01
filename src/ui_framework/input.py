"""
UI 输入事件管理器
处理按键输入并转换为事件
"""

import time

from machine import Pin


class InputManager:
    """输入管理器，处理按键和其他输入设备"""

    def __init__(self):
        """初始化输入管理器"""
        self.buttons = {}
        self.button_states = {}
        self.button_last_press = {}
        self.button_long_press_triggered = {}  # 记录长按是否已触发
        self.debounce_time = 0.05  # 防抖时间（秒）
        self.long_press_time = 0.5  # 长按时间（秒）
        self.event_queue = []

    def register_button(self, name, pin_num, pull=Pin.PULL_UP, inverted=True):
        """
        注册按钮

        Args:
            name: 按钮名称（如 'k1', 'up', 'ok' 等）
            pin_num: GPIO 引脚号
            pull: 上拉/下拉模式
            inverted: 是否反转逻辑（True表示按下为0，默认True）
        """
        pin = Pin(pin_num, Pin.IN, pull)
        self.buttons[name] = {
            "pin": pin,
            "inverted": inverted,
            "pressed": False,
            "press_time": 0,
        }
        self.button_states[name] = False
        self.button_last_press[name] = 0
        self.button_long_press_triggered[name] = False

    def _is_button_pressed(self, name):
        """检查按钮是否被按下"""
        if name not in self.buttons:
            return False

        btn = self.buttons[name]
        value = btn["pin"].value()

        # 如果是反转逻辑，0表示按下
        if btn["inverted"]:
            return value == 0
        else:
            return value == 1

    def update(self):
        """更新输入状态，检测按键变化并生成事件"""
        current_time = time.ticks_ms() / 1000.0

        for name, btn in self.buttons.items():
            is_pressed = self._is_button_pressed(name)
            was_pressed = btn["pressed"]

            # 检测按下事件
            if is_pressed and not was_pressed:
                # 防抖检查
                if current_time - self.button_last_press[name] > self.debounce_time:
                    btn["pressed"] = True
                    btn["press_time"] = current_time
                    self.button_last_press[name] = current_time

                    # 生成按键按下事件
                    self.event_queue.append({"type": "key_press", "key": name})

            # 检测释放事件
            elif not is_pressed and was_pressed:
                press_duration = current_time - btn["press_time"]
                btn["pressed"] = False

                # 生成按键释放事件
                self.event_queue.append(
                    {
                        "type": "key_release",
                        "key": name,
                        "duration": press_duration,
                    }
                )

                # 检查是否为点击事件（短按）
                if press_duration < self.long_press_time:
                    self.event_queue.append({"type": "key_click", "key": name})

                # 重置长按触发标志
                self.button_long_press_triggered[name] = False

            # 检测长按事件
            elif is_pressed and was_pressed:
                press_duration = current_time - btn["press_time"]
                # 只在达到长按时间且未触发过时触发一次
                if (
                    press_duration >= self.long_press_time
                    and not self.button_long_press_triggered[name]
                ):
                    self.button_long_press_triggered[name] = True
                    self.event_queue.append(
                        {
                            "type": "key_long_press",
                            "key": name,
                            "duration": press_duration,
                        }
                    )

    def poll_event(self):
        """
        获取下一个事件

        Returns:
            dict or None: 事件对象，如果没有事件则返回 None
        """
        if self.event_queue:
            return self.event_queue.pop(0)
        return None

    def has_events(self):
        """检查是否有待处理的事件"""
        return len(self.event_queue) > 0

    def clear_events(self):
        """清空事件队列"""
        self.event_queue = []

    def is_pressed(self, name):
        """
        检查按钮当前是否被按下

        Args:
            name: 按钮名称

        Returns:
            bool: 是否被按下
        """
        if name in self.buttons:
            return self.buttons[name]["pressed"]
        return False

    def get_press_duration(self, name):
        """
        获取按钮按下持续时间

        Args:
            name: 按钮名称

        Returns:
            float: 按下持续时间（秒），如果未按下则返回0
        """
        if name in self.buttons and self.buttons[name]["pressed"]:
            current_time = time.ticks_ms() / 1000.0
            return current_time - self.buttons[name]["press_time"]
        return 0


class KeyMapper:
    """按键映射器，将物理按键映射到逻辑按键"""

    def __init__(self):
        """初始化按键映射器"""
        self.key_map = {}
        self.context_stack = ["default"]

    def set_mapping(self, physical_key, logical_key, context="default"):
        """
        设置按键映射

        Args:
            physical_key: 物理按键名称（如 'k1'）
            logical_key: 逻辑按键名称（如 'up', 'ok', 'back'）
            context: 上下文名称（不同页面可使用不同映射）
        """
        if context not in self.key_map:
            self.key_map[context] = {}
        self.key_map[context][physical_key] = logical_key

    def push_context(self, context):
        """推入新的上下文"""
        self.context_stack.append(context)

    def pop_context(self):
        """弹出当前上下文"""
        if len(self.context_stack) > 1:
            self.context_stack.pop()

    def get_current_context(self):
        """获取当前上下文"""
        return self.context_stack[-1] if self.context_stack else "default"

    def map_key(self, physical_key):
        """
        映射物理按键到逻辑按键

        Args:
            physical_key: 物理按键名称

        Returns:
            str: 逻辑按键名称，如果没有映射则返回原始名称
        """
        context = self.get_current_context()

        # 先尝试当前上下文
        if context in self.key_map and physical_key in self.key_map[context]:
            return self.key_map[context][physical_key]

        # 回退到默认上下文
        if "default" in self.key_map and physical_key in self.key_map["default"]:
            return self.key_map["default"][physical_key]

        # 没有映射，返回原始名称
        return physical_key

    def translate_event(self, event):
        """
        翻译事件中的按键名称

        Args:
            event: 原始事件

        Returns:
            dict: 翻译后的事件
        """
        if event and "key" in event:
            translated_event = event.copy()
            translated_event["key"] = self.map_key(event["key"])
            translated_event["physical_key"] = event["key"]
            return translated_event
        return event
