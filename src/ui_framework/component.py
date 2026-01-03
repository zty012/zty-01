"""
UI 组件基类和常用组件实现
提供可复用的 UI 组件系统
"""

from easings import ease_out_expo


class Component:
    """UI 组件基类"""

    def __init__(self, x=0, y=0, width=128, height=64):
        """
        初始化组件

        Args:
            x: 组件 x 坐标
            y: 组件 y 坐标
            width: 组件宽度
            height: 组件高度
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.focused = False
        self.parent = None
        self.children = []

    def add_child(self, child):
        """添加子组件"""
        child.parent = self
        self.children.append(child)
        return child

    def remove_child(self, child):
        """移除子组件"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def render(self, display):
        """
        渲染组件（需要子类实现）

        Args:
            display: SSD1306 显示对象
        """
        if not self.visible:
            return

        # 渲染自己
        self._render_self(display)

        # 渲染所有子组件
        for child in self.children:
            child.render(display)

    def _render_self(self, display):
        """渲染组件自身（子类重写此方法）"""
        pass

    def handle_event(self, event):
        """
        处理事件

        Args:
            event: 事件对象 {'type': 'key_press', 'key': 'k1', ...}

        Returns:
            bool: 是否消费了该事件
        """
        # 先让子组件处理
        for child in reversed(self.children):  # 反向遍历，顶层优先
            if child.handle_event(event):
                return True

        # 子组件未处理，由自己处理
        return self._handle_self_event(event)

    def _handle_self_event(self, event):
        """处理组件自身的事件（子类重写此方法）"""
        return False

    def update(self, delta_time):
        """
        更新组件状态（用于动画等）

        Args:
            delta_time: 距离上次更新的时间差（秒）
        """
        for child in self.children:
            child.update(delta_time)


class Text(Component):
    """文本组件"""

    def __init__(self, text="", x=0, y=0, color=1):
        """
        初始化文本组件

        Args:
            text: 显示的文本
            x: x 坐标
            y: y 坐标
            color: 文本颜色 (0=黑, 1=白)
        """
        super().__init__(x, y)
        self.text = text
        self.color = color
        self.align = "left"  # left, center, right

    def _render_self(self, display):
        """渲染文本"""
        if not self.text:
            return

        x = self.x
        if self.align == "center":
            text_width = len(self.text) * 8
            x = self.x - text_width // 2
        elif self.align == "right":
            text_width = len(self.text) * 8
            x = self.x - text_width

        display.text(self.text, x, self.y, self.color)


class Box(Component):
    """矩形框组件"""

    def __init__(self, x=0, y=0, width=10, height=10, color=1, fill=False):
        """
        初始化矩形框

        Args:
            x, y: 左上角坐标
            width, height: 宽度和高度
            color: 边框颜色
            fill: 是否填充
        """
        super().__init__(x, y, width, height)
        self.color = color
        self.fill = fill

    def _render_self(self, display):
        """渲染矩形框"""
        display.rect(self.x, self.y, self.width, self.height, self.color, self.fill)


class Circle(Component):
    """圆形组件"""

    def __init__(self, x=0, y=0, radius=5, color=1, fill=False):
        """
        初始化圆形

        Args:
            x, y: 圆心坐标
            radius: 半径
            color: 颜色
            fill: 是否填充
        """
        super().__init__(x, y)
        self.radius = radius
        self.color = color
        self.fill = fill

    def _render_self(self, display):
        """渲染圆形"""
        display.ellipse(self.x, self.y, self.radius, self.radius, self.color, self.fill)


class ProgressBar(Component):
    """进度条组件"""

    def __init__(self, x=0, y=0, width=100, height=8, value=0, max_value=100):
        """
        初始化进度条

        Args:
            x, y: 左上角坐标
            width, height: 进度条尺寸
            value: 当前值
            max_value: 最大值
        """
        super().__init__(x, y, width, height)
        self.value = value
        self.max_value = max_value
        self.border = True

    def set_value(self, value):
        """设置进度值"""
        self.value = max(0, min(value, self.max_value))

    def _render_self(self, display):
        """渲染进度条"""
        # 绘制边框
        if self.border:
            display.rect(self.x, self.y, self.width, self.height, 1, False)

        # 计算填充宽度
        if self.max_value > 0:
            fill_width = int((self.value / self.max_value) * (self.width - 2))
            if fill_width > 0:
                display.fill_rect(
                    self.x + 1, self.y + 1, fill_width, self.height - 2, 1
                )


class Menu(Component):
    """菜单组件（带标题）"""

    def __init__(self, title, x=0, y=0, width=128, items=None):
        """
        初始化菜单

        Args:
            title: 菜单标题（必选）
            x, y: 左上角坐标
            width: 菜单宽度
            items: 菜单项列表 [{'label': '选项1', 'action': callback}, ...]
        """
        super().__init__(x, y, width)
        self.title = title
        self.items = items or []
        self.selected_index = 0
        self.title_height = 14  # 标题区域高度
        self.item_height = 12
        self.scroll_offset = 0
        self.max_visible_items = 4

        # 动画相关
        self.anim_enabled = True
        self.anim_duration = 0.2  # 动画时长（秒）
        self.anim_current_y = 0.0  # 当前高亮位置（相对于第一个可见项的偏移）
        self.anim_target_y = 0.0  # 目标高亮位置
        self.anim_time = 0.0  # 当前动画已经运行的时间
        self.anim_start_y = 0.0  # 动画开始时的位置

    def add_item(self, label, action=None):
        """添加菜单项"""
        self.items.append({"label": label, "action": action})

    def select_next(self):
        """选择下一项"""
        if self.selected_index < len(self.items) - 1:
            self.selected_index += 1
            # 自动滚动
            if self.selected_index >= self.scroll_offset + self.max_visible_items:
                self.scroll_offset += 1
                # 翻页时直接跳转，不做动画
                self.anim_current_y = float(self.selected_index - self.scroll_offset)
                self.anim_target_y = self.anim_current_y
            else:
                # 在可见范围内才做动画
                self._start_selection_animation()

    def select_prev(self):
        """选择上一项"""
        if self.selected_index > 0:
            self.selected_index -= 1
            # 自动滚动
            if self.selected_index < self.scroll_offset:
                self.scroll_offset -= 1
                # 翻页时直接跳转，不做动画
                self.anim_current_y = float(self.selected_index - self.scroll_offset)
                self.anim_target_y = self.anim_current_y
            else:
                # 在可见范围内才做动画
                self._start_selection_animation()

    def activate_selected(self):
        """激活当前选中项"""
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            if item.get("action"):
                item["action"]()
                return True
        return False

    def _start_selection_animation(self):
        """启动选项切换动画（支持流畅打断）"""
        if not self.anim_enabled:
            # 如果动画未启用，直接设置到目标位置
            self.anim_current_y = float(self.selected_index - self.scroll_offset)
            self.anim_target_y = self.anim_current_y
            return

        # 计算新的目标位置（相对于 scroll_offset）
        new_target = float(self.selected_index - self.scroll_offset)

        # 如果目标位置改变，启动新动画（从当前位置开始，实现流畅打断）
        if new_target != self.anim_target_y:
            self.anim_start_y = self.anim_current_y
            self.anim_target_y = new_target
            self.anim_time = 0.0

    def update(self, delta_time):
        """更新动画状态"""
        super().update(delta_time)

        if not self.anim_enabled:
            return

        # 更新选择框动画
        if self.anim_time < self.anim_duration:
            self.anim_time += delta_time

            # 限制时间不超过动画时长
            if self.anim_time >= self.anim_duration:
                self.anim_time = self.anim_duration

            # 计算动画进度 (0.0 - 1.0)
            progress = self.anim_time / self.anim_duration

            # 应用缓动函数
            eased_progress = ease_out_expo(progress)

            # 计算当前位置
            self.anim_current_y = (
                self.anim_start_y
                + (self.anim_target_y - self.anim_start_y) * eased_progress
            )
        else:
            # 动画已完成，确保在目标位置
            self.anim_current_y = self.anim_target_y

    def _render_self(self, display):
        """渲染菜单"""
        # 渲染标题（居中）
        title_text_width = len(self.title) * 8
        title_x = self.x + (self.width - title_text_width) // 2
        display.text(self.title, title_x, self.y + 2, 1)

        # 菜单项起始 Y 坐标
        menu_start_y = self.y + self.title_height

        visible_items = min(self.max_visible_items, len(self.items))

        # 绘制菜单项文本（所有文字都是白色）
        for i in range(visible_items):
            item_index = self.scroll_offset + i
            if item_index >= len(self.items):
                break

            item = self.items[item_index]
            y = menu_start_y + i * self.item_height

            # 绘制文本（始终白色）
            display.text(item["label"], self.x + 2, y + 2, 1)

        # 绘制动画高亮框框
        if self.anim_enabled:
            # 使用动画位置
            highlight_y = menu_start_y + int(self.anim_current_y * self.item_height)
        else:
            # 直接使用选中索引
            highlight_index = self.selected_index - self.scroll_offset
            highlight_y = menu_start_y + highlight_index * self.item_height

        # 绘制边框（不填充）
        display.rect(self.x, highlight_y, self.width, self.item_height, 1, False)

        # 绘制滚动指示器
        if len(self.items) > self.max_visible_items:
            # 显示向上箭头
            if self.scroll_offset > 0:
                display.text("^", self.x + self.width - 8, menu_start_y, 1)
            # 显示向下箭头
            if self.scroll_offset + self.max_visible_items < len(self.items):
                display.text(
                    "v",
                    self.x + self.width - 8,
                    menu_start_y + (visible_items - 1) * self.item_height,
                    1,
                )

    def _handle_self_event(self, event):
        """处理菜单事件"""
        if event.get("type") == "key_press":
            key = event.get("key")
            if key == "up":
                self.select_prev()
                return True
            elif key == "down":
                self.select_next()
                return True
            elif key == "ok":
                return self.activate_selected()
        return False


class Button(Component):
    """按钮组件"""

    def __init__(self, text="Button", x=0, y=0, width=60, height=16, action=None):
        """
        初始化按钮

        Args:
            text: 按钮文本
            x, y: 左上角坐标
            width, height: 按钮尺寸
            action: 点击回调函数
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.action = action
        self.pressed = False

    def press(self):
        """按下按钮"""
        self.pressed = True
        if self.action:
            self.action()

    def release(self):
        """释放按钮"""
        self.pressed = False

    def _render_self(self, display):
        """渲染按钮"""
        # 绘制边框和背景
        if self.pressed or self.focused:
            display.fill_rect(self.x, self.y, self.width, self.height, 1)
            text_color = 0
        else:
            display.rect(self.x, self.y, self.width, self.height, 1, False)
            text_color = 1

        # 居中绘制文本
        text_width = len(self.text) * 8
        text_x = self.x + (self.width - text_width) // 2
        text_y = self.y + (self.height - 8) // 2
        display.text(self.text, text_x, text_y, text_color)

    def _handle_self_event(self, event):
        """处理按钮事件"""
        if event.get("type") == "key_press" and event.get("key") == "ok":
            if self.focused:
                self.press()
                return True
        elif event.get("type") == "key_release" and event.get("key") == "ok":
            if self.focused:
                self.release()
                return True
        return False


class Icon(Component):
    """图标组件（使用简单的像素图案）"""

    def __init__(self, x=0, y=0, icon_data=None):
        """
        初始化图标

        Args:
            x, y: 左上角坐标
            icon_data: 图标数据，格式为 {'width': w, 'height': h, 'data': [...]}
        """
        super().__init__(x, y)
        self.icon_data = icon_data or {"width": 8, "height": 8, "data": []}

    def _render_self(self, display):
        """渲染图标"""
        if not self.icon_data or not self.icon_data.get("data"):
            return

        width = self.icon_data["width"]
        height = self.icon_data["height"]
        data = self.icon_data["data"]

        for row in range(height):
            if row >= len(data):
                break
            row_data = data[row]
            for col in range(width):
                if col < len(row_data) and row_data[col]:
                    display.pixel(self.x + col, self.y + row, 1)


class Label(Component):
    """标签组件（带边框的文本）"""

    def __init__(self, text="", x=0, y=0, width=60, height=16, border=True):
        """
        初始化标签

        Args:
            text: 标签文本
            x, y: 左上角坐标
            width, height: 标签尺寸
            border: 是否显示边框
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.border = border
        self.align = "left"  # left, center, right

    def _render_self(self, display):
        """渲染标签"""
        if self.border:
            display.rect(self.x, self.y, self.width, self.height, 1, False)

        # 绘制文本
        text_x = self.x + 2
        text_y = self.y + (self.height - 8) // 2

        if self.align == "center":
            text_width = len(self.text) * 8
            text_x = self.x + (self.width - text_width) // 2
        elif self.align == "right":
            text_width = len(self.text) * 8
            text_x = self.x + self.width - text_width - 2

        display.text(self.text, text_x, text_y, 1)
