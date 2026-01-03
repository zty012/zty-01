"""
键盘输入页面
提供 ASCII 字符输入功能
"""

from ui_framework.components.keyboard import Keyboard
from ui_framework.page import Page


class KeyboardPage(Page):
    """键盘输入页面"""

    def __init__(self, title="Input", default_value="", callback=None):
        """
        初始化键盘页面

        Args:
            title: 标题文本（必须）
            default_value: 默认输入值（可选）
            callback: 完成回调函数，接收输入文本作为参数（可选）
        """
        super().__init__("Keyboard")

        # 保存初始参数
        self._init_title = title
        self._init_default_value = default_value
        self._init_callback = callback

        # 创建键盘组件
        self.keyboard = Keyboard(
            title=title, default_value=default_value, callback=callback, x=0, y=0
        )
        self.add_component(self.keyboard)

    def on_enter(self, **kwargs):
        """
        页面进入时调用，支持动态参数

        Args:
            **kwargs: 可选参数
                title: 覆盖标题
                default_value: 覆盖默认值
                callback: 覆盖回调函数
        """
        super().on_enter(**kwargs)

        # 使用传入的参数更新键盘组件
        if "title" in kwargs:
            self.keyboard.title = kwargs["title"]
        else:
            self.keyboard.title = self._init_title

        if "default_value" in kwargs:
            self.keyboard.buffer = kwargs["default_value"]
        else:
            self.keyboard.buffer = self._init_default_value

        if "callback" in kwargs:
            self.keyboard.callback = kwargs["callback"]
        else:
            self.keyboard.callback = self._init_callback

        # 重置光标位置
        self.keyboard.cursor_x = 0
        self.keyboard.cursor_y = 0

    def _handle_page_event(self, event):
        """处理页面级事件"""
        # 键盘组件会处理所有事件，页面不需要额外处理
        return False

    def get_input(self):
        """获取当前输入的文本"""
        return self.keyboard.buffer

    def set_callback(self, callback):
        """设置回调函数"""
        self.keyboard.callback = callback
