"""
页面过渡动画系统
提供各种页面切换动画效果
"""

import framebuf


class Transition:
    """过渡动画基类"""

    def __init__(self, duration=0.3):
        """
        初始化过渡动画

        Args:
            duration: 动画持续时间（秒）
        """
        self.duration = duration
        self.elapsed = 0.0
        self.progress = 0.0  # 0.0 到 1.0
        self.finished = False

    def start(self, from_page, to_page, display):
        """
        开始动画

        Args:
            from_page: 源页面
            to_page: 目标页面
            display: 显示对象
        """
        self.elapsed = 0.0
        self.progress = 0.0
        self.finished = False
        self.from_page = from_page
        self.to_page = to_page
        self.display = display

        # 预渲染两个页面到缓冲区
        self._prepare_buffers()

    def _prepare_buffers(self):
        """准备页面缓冲区"""
        width = self.display.width
        height = self.display.height

        # 创建两个帧缓冲区
        self.from_buffer = bytearray(width * height // 8)
        self.to_buffer = bytearray(width * height // 8)

        # 创建 FrameBuffer 对象
        self.from_fb = framebuf.FrameBuffer(
            self.from_buffer, width, height, framebuf.MONO_HLSB
        )
        self.to_fb = framebuf.FrameBuffer(
            self.to_buffer, width, height, framebuf.MONO_HLSB
        )

        # 渲染源页面
        self.from_fb.fill(0)
        if self.from_page:
            for component in self.from_page.components:
                component.render(self.from_fb)

        # 渲染目标页面
        self.to_fb.fill(0)
        if self.to_page:
            for component in self.to_page.components:
                component.render(self.to_fb)

    def update(self, delta_time):
        """
        更新动画状态

        Args:
            delta_time: 时间增量（秒）
        """
        if self.finished:
            return

        self.elapsed += delta_time
        self.progress = min(1.0, self.elapsed / self.duration)

        if self.progress >= 1.0:
            self.finished = True

    def render(self):
        """渲染当前帧（子类必须实现）"""
        raise NotImplementedError

    def ease_in_out(self, t):
        """缓动函数：先加速后减速"""
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - pow(-2 * t + 2, 2) / 2

    def ease_out(self, t):
        """缓动函数：减速"""
        return 1 - (1 - t) * (1 - t)

    def reverse(self):
        """返回反向动画（子类可重写）"""
        # 默认返回无动画
        return NoTransition()


class SlideTransition(Transition):
    """滑动过渡动画"""

    def __init__(self, duration=0.3, direction="left"):
        """
        初始化滑动过渡

        Args:
            duration: 动画持续时间
            direction: 滑动方向 ("left", "right", "up", "down")
        """
        super().__init__(duration)
        self.direction = direction

    def render(self):
        """渲染滑动动画"""
        width = self.display.width
        height = self.display.height

        # 使用缓动函数
        t = self.ease_out(self.progress)

        # 清空显示
        self.display.fill(0)

        if self.direction == "left":
            # 向左滑动：旧页面以一半速度向左移动，新页面从右侧滑入（视差效果）
            from_x = int(-width * t * 0.5)  # 旧页面移动一半距离
            to_x = int(width * (1 - t))
            self.display.blit(self.from_fb, from_x, 0)
            self.display.blit(self.to_fb, to_x, 0)

        elif self.direction == "right":
            # 向右滑动：旧页面以一半速度向右移动，新页面从左侧滑入（视差效果）
            from_x = int(width * t * 0.5)  # 旧页面移动一半距离
            to_x = int(-width * (1 - t))
            self.display.blit(self.from_fb, from_x, 0)
            self.display.blit(self.to_fb, to_x, 0)

        elif self.direction == "up":
            # 向上滑动：旧页面以一半速度向上移动，新页面从下方滑入（视差效果）
            from_y = int(-height * t * 0.5)  # 旧页面移动一半距离
            to_y = int(height * (1 - t))
            self.display.blit(self.from_fb, 0, from_y)
            self.display.blit(self.to_fb, 0, to_y)

        elif self.direction == "down":
            # 向下滑动：旧页面以一半速度向下移动，新页面从上方滑入（视差效果）
            from_y = int(height * t * 0.5)  # 旧页面移动一半距离
            to_y = int(-height * (1 - t))
            self.display.blit(self.from_fb, 0, from_y)
            self.display.blit(self.to_fb, 0, to_y)

    def reverse(self):
        """返回反向的滑动动画"""
        reverse_directions = {
            "left": "right",
            "right": "left",
            "up": "down",
            "down": "up",
        }
        reverse_dir = reverse_directions.get(self.direction, self.direction)
        return SlideTransition(self.duration, reverse_dir)


class FadeTransition(Transition):
    """淡入淡出过渡动画（简化版，通过帧交替实现）"""

    def __init__(self, duration=0.3):
        super().__init__(duration)

    def render(self):
        """渲染淡入淡出动画"""
        # 在 OLED 上真正的淡入淡出需要灰度支持
        # 这里使用帧交替模拟淡入淡出效果
        t = self.progress

        self.display.fill(0)

        if t < 0.5:
            # 前半段：显示源页面，逐渐增加闪烁
            self.display.blit(self.from_fb, 0, 0)
        else:
            # 后半段：显示目标页面
            self.display.blit(self.to_fb, 0, 0)

    def reverse(self):
        """淡入淡出的反向也是淡入淡出"""
        return FadeTransition(self.duration)


class WipeTransition(Transition):
    """擦除过渡动画"""

    def __init__(self, duration=0.3, direction="left"):
        """
        初始化擦除过渡

        Args:
            duration: 动画持续时间
            direction: 擦除方向 ("left", "right", "up", "down")
        """
        super().__init__(duration)
        self.direction = direction

    def render(self):
        """渲染擦除动画"""
        width = self.display.width
        height = self.display.height
        t = self.ease_in_out(self.progress)

        self.display.fill(0)

        if self.direction == "left":
            # 从左到右擦除
            split_x = int(width * t)
            # 右侧显示旧页面
            if split_x < width:
                self._blit_region(self.from_fb, split_x, 0, width - split_x, height)
            # 左侧显示新页面
            if split_x > 0:
                self._blit_region(self.to_fb, 0, 0, split_x, height, dest_x=0)

        elif self.direction == "right":
            # 从右到左擦除
            split_x = int(width * (1 - t))
            # 左侧显示旧页面
            if split_x > 0:
                self._blit_region(self.from_fb, 0, 0, split_x, height)
            # 右侧显示新页面
            if split_x < width:
                self._blit_region(
                    self.to_fb, split_x, 0, width - split_x, height, dest_x=split_x
                )

        elif self.direction == "up":
            # 从上到下擦除
            split_y = int(height * t)
            # 下方显示旧页面
            if split_y < height:
                self._blit_region(self.from_fb, 0, split_y, width, height - split_y)
            # 上方显示新页面
            if split_y > 0:
                self._blit_region(self.to_fb, 0, 0, width, split_y, dest_y=0)

        elif self.direction == "down":
            # 从下到上擦除
            split_y = int(height * (1 - t))
            # 上方显示旧页面
            if split_y > 0:
                self._blit_region(self.from_fb, 0, 0, width, split_y)
            # 下方显示新页面
            if split_y < height:
                self._blit_region(
                    self.to_fb, 0, split_y, width, height - split_y, dest_y=split_y
                )

    def _blit_region(self, fb, src_x, src_y, w, h, dest_x=None, dest_y=None, key=-1):
        """
        复制帧缓冲区的指定区域

        Args:
            fb: 源帧缓冲区
            src_x, src_y: 源区域起始坐标
            w, h: 区域宽度和高度
            dest_x, dest_y: 目标坐标（默认与源坐标相同）
        """
        if dest_x is None:
            dest_x = src_x
        if dest_y is None:
            dest_y = src_y

        # 使用 blit 方法，但需要裁剪
        # 简化实现：直接 blit 整个帧缓冲区，然后用遮罩
        # 更高效的方法是逐行复制，但这里先用简单方法
        for y in range(h):
            for x in range(w):
                pixel = fb.pixel(src_x + x, src_y + y)
                self.display.pixel(dest_x + x, dest_y + y, pixel)

    def reverse(self):
        """返回反向的擦除动画"""
        reverse_directions = {
            "left": "right",
            "right": "left",
            "up": "down",
            "down": "up",
        }
        reverse_dir = reverse_directions.get(self.direction, self.direction)
        return WipeTransition(self.duration, reverse_dir)


class PushTransition(Transition):
    """推入过渡动画（新页面推入，旧页面被推出）"""

    def __init__(self, duration=0.3, direction="left"):
        """
        初始化推入过渡

        Args:
            duration: 动画持续时间
            direction: 推入方向 ("left", "right", "up", "down")
        """
        super().__init__(duration)
        self.direction = direction

    def render(self):
        """渲染推入动画"""
        width = self.display.width
        height = self.display.height
        t = self.ease_out(self.progress)

        self.display.fill(0)

        if self.direction == "left":
            # 向左推入
            offset = int(width * t)
            self.display.blit(self.from_fb, -offset, 0)
            self.display.blit(self.to_fb, width - offset, 0)

        elif self.direction == "right":
            # 向右推入
            offset = int(width * t)
            self.display.blit(self.from_fb, offset, 0)
            self.display.blit(self.to_fb, -width + offset, 0)

        elif self.direction == "up":
            # 向上推入
            offset = int(height * t)
            self.display.blit(self.from_fb, 0, -offset)
            self.display.blit(self.to_fb, 0, height - offset)

        elif self.direction == "down":
            # 向下推入
            offset = int(height * t)
            self.display.blit(self.from_fb, 0, offset)
            self.display.blit(self.to_fb, 0, -height + offset)

    def reverse(self):
        """返回反向的推入动画"""
        reverse_directions = {
            "left": "right",
            "right": "left",
            "up": "down",
            "down": "up",
        }
        reverse_dir = reverse_directions.get(self.direction, self.direction)
        return PushTransition(self.duration, reverse_dir)


class NoTransition(Transition):
    """无过渡动画（立即切换）"""

    def __init__(self):
        super().__init__(duration=0.0)

    def start(self, from_page, to_page, display):
        """开始动画"""
        self.to_page = to_page
        self.display = display
        self.finished = True

    def render(self):
        """直接渲染目标页面"""
        self.display.fill(0)
        if self.to_page:
            for component in self.to_page.components:
                component.render(self.display)

    def reverse(self):
        """无动画的反向也是无动画"""
        return NoTransition()
