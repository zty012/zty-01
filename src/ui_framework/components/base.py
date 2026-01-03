"""
UI 组件基类
"""


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
