"""
IP地址输入组件
支持IPv4地址输入（xxx.xxx.xxx.xxx）
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


class IPInput(Component):
    """IP地址输入组件"""

    def __init__(
        self, title="IP Address", default_value="0.0.0.0", callback=None, x=0, y=0
    ):
        """
        初始化IP地址输入组件

        Args:
            title: 标题文本
            default_value: 默认IP地址（格式：xxx.xxx.xxx.xxx）
            callback: 完成回调函数，接收IP地址字符串作为参数
            x: x 坐标
            y: y 坐标
        """
        super().__init__(x, y, width=128, height=64)

        self.title = title
        self.callback = callback

        # 解析默认值
        self.segments = [0, 0, 0, 0]
        try:
            parts = default_value.split(".")
            for i in range(min(4, len(parts))):
                val = int(parts[i])
                self.segments[i] = max(0, min(255, val))
        except:
            self.segments = [0, 0, 0, 0]

        # 当前编辑的段索引（0-3）
        self.current_segment = 0

        # 光标闪烁
        self.cursor_blink_time = 0
        self.cursor_blink_interval = 0.5
        self.cursor_visible = True

        # 布局参数
        self.title_y = 0
        self.ip_y = 20
        self.hint_y = 54

    def get_ip_string(self):
        """获取IP地址字符串"""
        return "{}.{}.{}.{}".format(
            self.segments[0], self.segments[1], self.segments[2], self.segments[3]
        )

    def move_segment_left(self):
        """向左移动段"""
        if self.current_segment > 0:
            self.current_segment -= 1

    def move_segment_right(self):
        """向右移动段"""
        if self.current_segment < 3:
            self.current_segment += 1

    def increment_value(self):
        """增加当前段的值"""
        self.segments[self.current_segment] = (
            self.segments[self.current_segment] + 1
        ) % 256

    def decrement_value(self):
        """减少当前段的值"""
        self.segments[self.current_segment] = (
            self.segments[self.current_segment] - 1
        ) % 256

    def increment_value_fast(self):
        """快速增加当前段的值（+10）"""
        self.segments[self.current_segment] = (
            self.segments[self.current_segment] + 10
        ) % 256

    def decrement_value_fast(self):
        """快速减少当前段的值（-10）"""
        self.segments[self.current_segment] = (
            self.segments[self.current_segment] - 10
        ) % 256

    def confirm_input(self):
        """确认输入"""
        if self.callback:
            self.callback(self.get_ip_string())

    def update(self, delta_time):
        """更新组件状态"""
        super().update(delta_time)

        # 更新光标闪烁
        self.cursor_blink_time += delta_time
        if self.cursor_blink_time >= self.cursor_blink_interval:
            self.cursor_blink_time = 0
            self.cursor_visible = not self.cursor_visible

    def _render_self(self, display):
        """渲染IP地址输入界面"""
        # 渲染标题
        title_x = (128 - len(self.title) * 8) // 2
        display.text(self.title, title_x, self.title_y, 1)

        # 渲染IP地址
        ip_str = self.get_ip_string()
        ip_x = (128 - len(ip_str) * 8) // 2
        display.text(ip_str, ip_x, self.ip_y, 1)

        # 渲染光标（在当前段下方）
        if self.cursor_visible:
            # 计算当前段在字符串中的位置
            segment_str = str(self.segments[self.current_segment])

            # 计算前面段的字符数（包括小数点）
            chars_before = 0
            for i in range(self.current_segment):
                chars_before += len(str(self.segments[i])) + 1  # +1 for dot

            # 绘制下划线
            cursor_x = ip_x + chars_before * 8
            cursor_width = len(segment_str) * 8
            display.hline(cursor_x, self.ip_y + 9, cursor_width, 1)

        # 渲染提示信息
        hint = "^v:Val <>:Seg"
        hint_x = (128 - len(hint) * 8) // 2
        display.text(hint, hint_x, self.hint_y, 1)

    def _handle_self_event(self, event):
        """处理事件"""
        event_type = event.get("type")
        key = event.get("key")

        # 处理短按事件
        if event_type == "key_press":
            if key == "up":
                self.increment_value()
                return True
            elif key == "down":
                self.decrement_value()
                return True
            elif key == "back":
                self.move_segment_left()
                return True
            elif key == "ok":
                self.move_segment_right()
                return True

        # 处理长按事件
        elif event_type == "key_long_press":
            if key == "ok":
                # 长按 OK：下一段（循环）
                self.move_segment_left()
                return True
            elif key == "back":
                # 长按 BACK：确认输入
                self.move_segment_right()
                self.confirm_input()
                return True
            elif key == "down":
                # 长按 DOWN：取消输入
                self.decrement_value()
                if self.callback:
                    self.callback(None)
                return True
            elif key == "up":
                # 长按 UP：快速增加（+10）
                self.increment_value()
                self.increment_value_fast()
                return True

        return False
