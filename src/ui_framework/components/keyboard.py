"""
键盘组件
支持 ASCII 字符输入的虚拟键盘
"""

import time

from ui_framework.components.base import Component


def get_time_ms():
    """获取当前时间（毫秒）- 兼容 MicroPython 和标准 Python"""
    try:
        # MicroPython
        return time.ticks_ms()  # type: ignore
    except AttributeError:
        # Standard Python
        return int(time.time() * 1000)


class Keyboard(Component):
    """ASCII 字符键盘组件"""

    def __init__(self, title="Input", default_value="", callback=None, x=0, y=0):
        """
        初始化键盘组件

        Args:
            title: 标题文本
            default_value: 默认输入值
            callback: 完成回调函数，接收输入文本作为参数
            x: x 坐标
            y: y 坐标
        """
        super().__init__(x, y, width=128, height=64)

        self.title = title
        self.buffer = default_value
        self.callback = callback

        # ASCII 字符集（可打印字符）
        self.chars = []
        # 空格 (32)
        self.chars.append(" ")
        # 0-9 (48-57)
        for i in range(48, 58):
            self.chars.append(chr(i))
        # A-Z (65-90)
        for i in range(65, 91):
            self.chars.append(chr(i))
        # a-z (97-122)
        for i in range(97, 123):
            self.chars.append(chr(i))
        # 常用符号
        symbols = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        for s in symbols:
            self.chars.append(s)

        # 字符矩阵布局配置
        self.cols = 16  # 每行16个字符
        self.rows = (len(self.chars) + self.cols - 1) // self.cols

        # 光标位置（在字符矩阵中）
        self.cursor_x = 0
        self.cursor_y = 0

        # 光标闪烁
        self.cursor_blink_time = 0
        self.cursor_blink_interval = 0.5
        self.cursor_visible = True

        # 布局参数
        self.title_y = 0
        self.buffer_y = 10
        self.matrix_y = 20
        self.char_width = 8
        self.char_height = 8

    def get_current_char(self):
        """获取当前光标位置的字符"""
        index = self.cursor_y * self.cols + self.cursor_x
        if 0 <= index < len(self.chars):
            return self.chars[index]
        return None

    def move_cursor_up(self):
        """向上移动光标"""
        if self.cursor_y > 0:
            self.cursor_y -= 1

    def move_cursor_down(self):
        """向下移动光标"""
        if self.cursor_y < self.rows - 1:
            # 确保不会超出字符范围
            new_index = (self.cursor_y + 1) * self.cols + self.cursor_x
            if new_index < len(self.chars):
                self.cursor_y += 1

    def move_cursor_left(self):
        """向左移动光标"""
        if self.cursor_x > 0:
            self.cursor_x -= 1
        elif self.cursor_y > 0:
            # 换到上一行末尾
            self.cursor_y -= 1
            self.cursor_x = self.cols - 1
            # 确保不会超出字符范围
            index = self.cursor_y * self.cols + self.cursor_x
            while index >= len(self.chars) and self.cursor_x > 0:
                self.cursor_x -= 1
                index = self.cursor_y * self.cols + self.cursor_x

    def move_cursor_right(self):
        """向右移动光标"""
        index = self.cursor_y * self.cols + self.cursor_x
        if index < len(self.chars) - 1:
            self.cursor_x += 1
            if self.cursor_x >= self.cols:
                self.cursor_x = 0
                self.cursor_y += 1

    def add_char(self):
        """添加当前字符到缓冲区"""
        char = self.get_current_char()
        if char is not None:
            self.buffer += char

    def backspace(self):
        """删除最后一个字符"""
        if len(self.buffer) > 0:
            self.buffer = self.buffer[:-1]

    def confirm_input(self):
        """确认输入"""
        if self.callback:
            self.callback(self.buffer)

    def update(self, delta_time):
        """更新组件状态"""
        super().update(delta_time)

        # 更新光标闪烁
        self.cursor_blink_time += delta_time
        if self.cursor_blink_time >= self.cursor_blink_interval:
            self.cursor_blink_time = 0
            self.cursor_visible = not self.cursor_visible

    def _render_self(self, display):
        """渲染键盘"""
        # 渲染标题
        title_x = (128 - len(self.title) * 8) // 2
        display.text(self.title, title_x, self.title_y, 1)

        # 渲染缓冲区（输入文本）
        # 只显示最后15个字符
        display_buffer = self.buffer[-15:] if len(self.buffer) > 15 else self.buffer
        buffer_x = 0
        display.text(display_buffer, buffer_x, self.buffer_y, 1)

        # 渲染光标在缓冲区
        if self.cursor_visible and len(display_buffer) < 16:
            cursor_x = buffer_x + len(display_buffer) * 8
            display.text("_", cursor_x, self.buffer_y, 1)

        # 渲染字符矩阵
        visible_rows = 5  # 一次显示5行
        start_row = max(0, min(self.cursor_y - 2, self.rows - visible_rows))
        end_row = min(self.rows, start_row + visible_rows)

        for row in range(start_row, end_row):
            for col in range(self.cols):
                index = row * self.cols + col
                if index >= len(self.chars):
                    break

                char = self.chars[index]
                x = col * self.char_width
                y = self.matrix_y + (row - start_row) * self.char_height

                # 高亮当前光标位置
                if row == self.cursor_y and col == self.cursor_x:
                    # 绘制反色背景
                    display.fill_rect(x, y, self.char_width, self.char_height, 1)
                    display.text(char, x, y, 0)
                else:
                    display.text(char, x, y, 1)

    def _handle_self_event(self, event):
        """处理键盘事件"""
        event_type = event.get("type")
        key = event.get("key")

        # 处理短按事件 - 移动光标
        if event_type == "key_press":
            if key == "up":
                self.move_cursor_up()
                return True
            elif key == "down":
                self.move_cursor_down()
                return True
            elif key == "back":
                self.move_cursor_left()
                return True
            elif key == "ok":
                self.move_cursor_right()
                return True

        # 处理长按事件（InputManager 已保证每次长按只触发一次）
        elif event_type == "key_long_press":
            if key == "ok":
                # 长按 OK：添加字符
                self.move_cursor_left()
                self.add_char()
                return True
            elif key == "back":
                # 长按 BACK：确认输入
                self.move_cursor_right()
                self.confirm_input()
                return True
            elif key == "down":
                # 长按 DOWN：取消输入
                self.move_cursor_up()
                if self.callback:
                    self.callback(None)
                return True
            elif key == "up":
                # 长按 UP：退格
                self.move_cursor_down()
                self.backspace()
                return True

        return False
