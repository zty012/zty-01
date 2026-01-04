"""
Flappy Bird 游戏页面
按键说明：
- ok: 跳跃
- 长按 back: 暂停游戏（切换到暂停页面）
"""

import random
import time

from ui_framework.components.menu import Menu
from ui_framework.components.text import Text
from ui_framework.page import Page


class FlappyBirdPage(Page):
    """Flappy Bird 游戏主页面"""

    def __init__(self):
        super().__init__("FlappyBird")

        # 游戏区域设置 (128x64 屏幕)
        self.screen_width = 128
        self.screen_height = 64

        # 鸟的设置
        self.bird_radius = 3  # 圆形鸟的半径
        self.bird_x = 30  # 鸟的 x 坐标（固定）
        self.bird_y = 32  # 鸟的 y 坐标
        self.bird_velocity = 0  # 鸟的垂直速度
        self.gravity = 0.3  # 重力加速度
        self.jump_strength = -2.8  # 跳跃力度

        # 管道设置
        self.pipe_width = 12  # 管道宽度
        self.pipe_gap = 32  # 管道间隙
        self.pipe_speed = 1.5  # 管道移动速度
        self.pipes = []  # 管道列表 [(x, gap_y), ...]
        self.pipe_spawn_distance = 70  # 管道生成距离

        # 游戏状态
        self.score = 0
        self.game_over = False
        self.game_over_triggered = False  # 防止重复触发游戏结束页面
        self.game_started = False  # 游戏是否已开始

        # 初始化游戏
        self.reset_game()

    def reset_game(self):
        """重置游戏"""
        self.bird_y = self.screen_height // 2
        self.bird_velocity = 0
        self.score = 0
        self.game_over = False
        self.game_over_triggered = False
        self.game_started = False
        self.pipes = []

        # 生成初始管道
        for i in range(3):
            x = self.screen_width + i * self.pipe_spawn_distance
            gap_y = random.randint(20, self.screen_height - 20)
            self.pipes.append([x, gap_y])

    def jump(self):
        """鸟跳跃"""
        if not self.game_over:
            # 第一次按键时开始游戏
            if not self.game_started:
                self.game_started = True
            self.bird_velocity = self.jump_strength

    def update(self, delta_time):
        """游戏逻辑更新"""
        super().update(delta_time)

        if not self.active:
            return

        if self.game_over and not self.game_over_triggered:
            # 游戏结束，切换到游戏结束页面
            self.game_over_triggered = True
            self.goto_game_over()
            return

        if self.game_over:
            # 已经进入游戏结束页面，不再更新
            return

        # 游戏未开始时不更新
        if not self.game_started:
            return

        # 更新鸟的位置
        self.bird_velocity += self.gravity
        self.bird_y += self.bird_velocity

        # 检查鸟是否碰到上下边界
        if (
            self.bird_y - self.bird_radius <= 0
            or self.bird_y + self.bird_radius >= self.screen_height
        ):
            self.game_over = True
            return

        # 更新管道位置
        for pipe in self.pipes:
            pipe[0] -= self.pipe_speed

        # 移除屏幕外的管道并生成新管道
        if self.pipes and self.pipes[0][0] < -self.pipe_width:
            self.pipes.pop(0)
            self.score += 1
            # 生成新管道
            last_pipe_x = self.pipes[-1][0]
            new_x = last_pipe_x + self.pipe_spawn_distance
            gap_y = random.randint(20, self.screen_height - 20)
            self.pipes.append([new_x, gap_y])

        # 检查碰撞
        self.check_collision()

    def check_collision(self):
        """检查碰撞"""
        bird_left = self.bird_x - self.bird_radius
        bird_right = self.bird_x + self.bird_radius
        bird_top = self.bird_y - self.bird_radius
        bird_bottom = self.bird_y + self.bird_radius

        for pipe_x, gap_y in self.pipes:
            # 检查是否在管道的 x 范围内
            if bird_right >= pipe_x and bird_left <= pipe_x + self.pipe_width:
                # 检查是否碰到上方或下方管道
                gap_top = gap_y - self.pipe_gap // 2
                gap_bottom = gap_y + self.pipe_gap // 2

                if bird_top <= gap_top or bird_bottom >= gap_bottom:
                    self.game_over = True
                    return

    def goto_pause(self):
        """进入暂停页面"""
        if self.manager:
            self.manager.push_page(FlappyBirdPausePage(self))

    def goto_game_over(self):
        """进入游戏结束页面"""
        if self.manager:
            self.manager.push_page(FlappyBirdGameOverPage(self))

    def render(self, display):
        """绘制游戏画面"""
        super().render(display)

        # 绘制管道
        for pipe_x, gap_y in self.pipes:
            gap_top = gap_y - self.pipe_gap // 2
            gap_bottom = gap_y + self.pipe_gap // 2

            # 上方管道
            if gap_top > 0:
                display.fill_rect(int(pipe_x), 0, self.pipe_width, int(gap_top), 1)

            # 下方管道
            if gap_bottom < self.screen_height:
                display.fill_rect(
                    int(pipe_x),
                    int(gap_bottom),
                    self.pipe_width,
                    self.screen_height - int(gap_bottom),
                    1,
                )

        # 绘制鸟（圆形）
        self.draw_circle(
            display, int(self.bird_x), int(self.bird_y), self.bird_radius, 1
        )

        # 显示分数（左上角）
        score_str = f"Score: {self.score}"
        display.text(score_str, 2, 2, 1)

        # 游戏未开始时显示提示
        if not self.game_started:
            hint_str = "Press OK to Start"
            # 计算居中位置
            text_width = len(hint_str) * 8
            x = (self.screen_width - text_width) // 2
            y = self.screen_height // 2 + 10
            display.text(hint_str, x, y, 1)

    def draw_circle(self, display, cx, cy, radius, color):
        """绘制圆形（使用中点圆算法）"""
        x = radius
        y = 0
        err = 0

        while x >= y:
            # 绘制八个对称点
            display.pixel(cx + x, cy + y, color)
            display.pixel(cx + y, cy + x, color)
            display.pixel(cx - y, cy + x, color)
            display.pixel(cx - x, cy + y, color)
            display.pixel(cx - x, cy - y, color)
            display.pixel(cx - y, cy - x, color)
            display.pixel(cx + y, cy - x, color)
            display.pixel(cx + x, cy - y, color)

            if err <= 0:
                y += 1
                err += 2 * y + 1

            if err > 0:
                x -= 1
                err -= 2 * x + 1

        # 填充圆形
        for i in range(-radius, radius + 1):
            h = int((radius * radius - i * i) ** 0.5)
            for j in range(-h, h + 1):
                display.pixel(cx + i, cy + j, color)

    def _handle_page_event(self, event):
        """处理页面事件"""
        event_type = event.get("type")
        key = event.get("key")

        if event_type == "key_press":
            if key == "ok":
                self.jump()
                return True
            elif key == "back":
                # 按一下 back 键暂停游戏
                if self.game_started and not self.game_over:
                    self.goto_pause()
                return True

        return False

    def on_enter(self):
        """进入页面时"""
        super().on_enter()
        # 如果游戏结束了，重置游戏
        if self.game_over:
            self.reset_game()

    def on_exit(self):
        """退出页面时"""
        super().on_exit()

    def on_resume(self):
        """从暂停或游戏结束页面返回"""
        super().on_resume()


class FlappyBirdPausePage(Page):
    """Flappy Bird 暂停页面"""

    def __init__(self, game_page):
        super().__init__("FlappyBirdPause")
        self.game_page = game_page

        # 创建暂停菜单
        self.menu = Menu("PAUSED", x=0, y=0, width=128)
        self.menu.add_item("Continue", self.continue_game)
        self.menu.add_item("Restart", self.restart_game)
        self.menu.add_item("Exit", self.exit_game)
        self.add_component(self.menu)

    def continue_game(self):
        """继续游戏"""
        if self.manager:
            self.manager.pop_page()

    def restart_game(self):
        """重新开始游戏"""
        self.game_page.reset_game()
        if self.manager:
            self.manager.pop_page()

    def exit_game(self):
        """退出游戏"""
        if self.manager:
            # 退出暂停页面和游戏页面
            self.manager.pop_page()  # 退出暂停页面
            self.manager.pop_page()  # 退出游戏页面

    def _handle_page_event(self, event):
        """处理页面事件"""
        if event.get("type") == "key_press":
            key = event.get("key")
            if key == "up":
                self.menu.select_prev()
                return True
            elif key == "down":
                self.menu.select_next()
                return True
            elif key == "ok":
                return self.menu.activate_selected()
            elif key == "back":
                # back 键也可以继续游戏
                self.continue_game()
                return True
        return False


class FlappyBirdGameOverPage(Page):
    """Flappy Bird 游戏结束页面"""

    def __init__(self, game_page):
        super().__init__("FlappyBirdGameOver")
        self.game_page = game_page

        # 显示分数
        self.score_text = Text("", x=64, y=8)
        self.score_text.align = "center"
        self.add_component(self.score_text)

        # 创建游戏结束菜单
        self.menu = Menu("GAME OVER", x=0, y=20, width=128)
        self.menu.add_item("Restart", self.restart_game)
        self.menu.add_item("Exit", self.exit_game)
        self.add_component(self.menu)

    def restart_game(self):
        """重新开始游戏"""
        self.game_page.reset_game()
        if self.manager:
            self.manager.pop_page()

    def exit_game(self):
        """退出游戏"""
        if self.manager:
            # 退出游戏结束页面和游戏页面
            self.manager.pop_page()  # 退出游戏结束页面
            self.manager.pop_page()  # 退出游戏页面

    def on_enter(self):
        """进入页面时更新分数"""
        super().on_enter()
        self.score_text.text = f"Score: {self.game_page.score}"

    def _handle_page_event(self, event):
        """处理页面事件"""
        if event.get("type") == "key_press":
            key = event.get("key")
            if key == "up":
                self.menu.select_prev()
                return True
            elif key == "down":
                self.menu.select_next()
                return True
            elif key == "ok":
                return self.menu.activate_selected()
            elif key == "back":
                # back 键退出游戏
                self.exit_game()
                return True
        return False
