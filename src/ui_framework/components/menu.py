"""
菜单组件
"""

from easings import ease_out_expo
from ui_framework.components.base import Component


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
