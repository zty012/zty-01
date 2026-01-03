"""
UI 页面管理系统
提供页面切换、生命周期管理等功能
"""


class Page:
    """页面基类"""

    def __init__(self, name="Page"):
        """
        初始化页面

        Args:
            name: 页面名称
        """
        self.name = name
        self.components = []
        self.manager = None  # type: PageManager | None
        self.active = False

    def add_component(self, component):
        """添加组件到页面"""
        self.components.append(component)
        return component

    def remove_component(self, component):
        """从页面移除组件"""
        if component in self.components:
            self.components.remove(component)

    def on_enter(self, **kwargs):
        """
        页面进入时调用（子类可重写）

        Args:
            **kwargs: 传递给页面的参数
        """
        self.active = True

    def on_exit(self):
        """页面退出时调用（子类可重写）"""
        self.active = False

    def on_pause(self):
        """页面暂停时调用（如进入子页面）"""
        pass

    def on_resume(self):
        """页面恢复时调用（如从子页面返回）"""
        pass

    def update(self, delta_time):
        """
        更新页面状态

        Args:
            delta_time: 距离上次更新的时间差（秒）
        """
        if not self.active:
            return

        for component in self.components:
            component.update(delta_time)

    def render(self, display):
        """
        渲染页面

        Args:
            display: SSD1306 显示对象
        """
        if not self.active:
            return

        # 清空显示
        display.fill(0)

        # 渲染所有组件
        for component in self.components:
            component.render(display)

    def handle_event(self, event):
        """
        处理事件

        Args:
            event: 事件对象

        Returns:
            bool: 是否消费了该事件
        """
        if not self.active:
            return False

        # 让组件处理事件
        for component in reversed(self.components):  # 反向遍历，顶层优先
            if component.handle_event(event):
                return True

        # 组件未处理，由页面自己处理
        return self._handle_page_event(event)

    def _handle_page_event(self, event):
        """处理页面级事件（子类可重写）"""
        return False


class PageManager:
    """页面管理器"""

    def __init__(self, display):
        """
        初始化页面管理器

        Args:
            display: SSD1306 显示对象
        """
        self.display = display
        self.pages = {}
        self.page_stack = []
        self.current_page = None

    def register_page(self, name, page):
        """
        注册页面

        Args:
            name: 页面名称
            page: 页面对象
        """
        self.pages[name] = page
        page.manager = self
        return page

    def goto_page(self, name, clear_stack=False, **kwargs):
        """
        切换到指定页面

        Args:
            name: 页面名称或页面实例
            clear_stack: 是否清空页面栈（用于切换主页面）
            **kwargs: 传递给页面的参数
        """
        # 支持传入页面实例
        if isinstance(name, Page):
            page = name
            # 为页面实例设置 manager
            page.manager = self  # type: ignore
        elif name in self.pages:
            page = self.pages[name]
        else:
            print(f"Warning: Page '{name}' not found")
            return False

        # 退出当前页面
        if self.current_page:
            self.current_page.on_exit()

        # 清空栈或保存当前页面
        if clear_stack:
            self.page_stack = []
        elif self.current_page:
            self.page_stack.append(self.current_page)

        # 进入新页面
        self.current_page = page
        self.current_page.on_enter(**kwargs)
        return True

    def push_page(self, name, **kwargs):
        """
        推入新页面到栈顶（保留上一个页面）

        Args:
            name: 页面名称或页面实例
            **kwargs: 传递给页面的参数
        """
        # 支持传入页面实例
        if isinstance(name, Page):
            page = name
            # 为页面实例设置 manager
            page.manager = self  # type: ignore
        elif name in self.pages:
            page = self.pages[name]
        else:
            print(f"Warning: Page '{name}' not found")
            return False

        # 暂停当前页面
        if self.current_page:
            self.current_page.on_pause()
            self.page_stack.append(self.current_page)

        # 进入新页面
        self.current_page = page
        self.current_page.on_enter(**kwargs)
        return True

    def pop_page(self):
        """
        弹出当前页面，返回上一个页面
        """
        if not self.page_stack:
            print("Warning: No page to pop")
            return False

        # 退出当前页面
        if self.current_page:
            self.current_page.on_exit()

        # 恢复上一个页面
        self.current_page = self.page_stack.pop()
        self.current_page.on_resume()
        return True

    def back(self):
        """返回上一页（pop_page 的别名）"""
        return self.pop_page()

    def update(self, delta_time):
        """
        更新当前页面

        Args:
            delta_time: 距离上次更新的时间差（秒）
        """
        if self.current_page:
            self.current_page.update(delta_time)

    def render(self):
        """渲染当前页面"""
        if self.current_page:
            self.current_page.render(self.display)
            self.display.show()

    def handle_event(self, event):
        """
        处理事件

        Args:
            event: 事件对象

        Returns:
            bool: 是否消费了该事件
        """
        if self.current_page:
            return self.current_page.handle_event(event)
        return False

    def get_current_page(self):
        """获取当前页面"""
        return self.current_page

    def get_page_stack_depth(self):
        """获取页面栈深度"""
        return len(self.page_stack)
