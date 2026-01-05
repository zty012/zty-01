"""
IP地址输入页面
提供IPv4地址输入功能
"""

from ui_framework.components.ipinput import IPInput
from ui_framework.page import Page


class IPInputPage(Page):
    """IP地址输入页面"""

    def __init__(self, title="IP Address", default_value="0.0.0.0", callback=None):
        """
        初始化IP地址输入页面

        Args:
            title: 标题文本（必须）
            default_value: 默认IP地址（可选）
            callback: 完成回调函数，接收IP地址字符串作为参数（可选）
        """
        super().__init__("IPInput")

        # 保存初始参数
        self._init_title = title
        self._init_default_value = default_value
        self._init_callback = callback

        # 创建IP地址输入组件
        self.ipinput = IPInput(
            title=title, default_value=default_value, callback=self._callback, x=0, y=0
        )
        self.add_component(self.ipinput)

    def _callback(self, ip_address):
        """内部回调函数，调用用户提供的回调"""
        if self._init_callback and ip_address is not None:
            self._init_callback(ip_address)
        if self.manager:
            self.manager.pop_page()

    def on_enter(self, **kwargs):
        """
        页面进入时调用
        """
        super().on_enter(**kwargs)

        # 重置光标位置
        self.ipinput.current_segment = 0

    def _handle_page_event(self, event):
        """处理页面级事件"""
        # IP输入组件会处理所有事件，页面不需要额外处理
        return False

    def get_input(self):
        """获取当前输入的IP地址"""
        return self.ipinput.get_ip_string()

    def set_callback(self, callback):
        """设置回调函数"""
        self.ipinput.callback = callback
