"""
贪吃蛇游戏页面
按键说明：
- up: 向上
- down: 向下
- back: 向左
- ok: 向右
- 长按 back: 暂停游戏（切换到暂停页面）
"""

import random
import time

from ui_framework.components.menu import Menu
from ui_framework.components.text import Text
from ui_framework.page import Page


class SnakeGamePage(Page):
    """贪吃蛇游戏主页面"""

    def __init__(self):
        super().__init__("SnakeGame")

        # 游戏区域设置 (128x64 屏幕)
        self.grid_size = 4  # 每个格子的像素大小
        self.grid_width = 32  # 128 / 4
        self.grid_height = 16  # 64 / 4

        # 游戏状态
        self.snake = []  # 蛇的身体坐标列表 [(x, y), ...]
        self.direction = (1, 0)  # 当前方向 (dx, dy)
        self.next_direction = (1, 0)  # 下一个方向
        self.food = (0, 0)  # 食物位置
        self.score = 0
        self.game_over = False
        self.game_over_triggered = False  # 防止重复触发游戏结束页面

        # 游戏速度控制
        self.move_interval = 0.15  # 移动间隔（秒）
        self.move_timer = 0

        # 按键长按检测
        self.back_key_pressed = False
        self.back_key_press_time = 0
        self.long_press_threshold = 0.5  # 长按阈值（秒）

        # 初始化游戏
        self.reset_game()

    def reset_game(self):
        """重置游戏"""
        # 初始化蛇（从中间开始，长度为3）
        start_x = self.grid_width // 2
        start_y = self.grid_height // 2
        self.snake = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y),
        ]

        self.direction = (1, 0)  # 向右
        self.next_direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.game_over_triggered = False
        self.move_timer = 0
        self.move_interval = 0.15  # 重置速度

        # 生成第一个食物
        self.spawn_food()

    def spawn_food(self):
        """生成食物（避开边缘1格）"""
        # 找到所有空位置（避开最外层格子）
        empty_positions = []
        for x in range(1, self.grid_width - 1):  # 避开边缘
            for y in range(1, self.grid_height - 1):  # 避开边缘
                if (x, y) not in self.snake:
                    empty_positions.append((x, y))

        if empty_positions:
            self.food = random.choice(empty_positions)
        else:
            # 赢了！（填满整个屏幕）
            self.game_over = True

    def change_direction(self, new_direction):
        """改变方向（不能反向移动）"""
        if self.game_over:
            return

        dx, dy = new_direction
        curr_dx, curr_dy = self.direction

        # 防止反向移动
        if (dx + curr_dx, dy + curr_dy) != (0, 0):
            self.next_direction = new_direction

    def update(self, delta_time):
        """游戏逻辑更新"""
        super().update(delta_time)

        if not self.active:
            return

        # 检测 back 键长按
        if self.back_key_pressed:
            self.back_key_press_time += delta_time
            if self.back_key_press_time >= self.long_press_threshold:
                # 触发长按事件 - 进入暂停页面
                self.goto_pause()
                self.back_key_pressed = False  # 防止重复触发

        if self.game_over and not self.game_over_triggered:
            # 游戏结束，切换到游戏结束页面
            self.game_over_triggered = True
            self.goto_game_over()
            return

        if self.game_over:
            # 已经进入游戏结束页面，不再更新
            return

        # 移动计时器
        self.move_timer += delta_time
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            self.move_snake()

    def goto_pause(self):
        """进入暂停页面"""
        if self.manager:
            self.manager.push_page("snake_pause")

    def goto_game_over(self):
        """进入游戏结束页面"""
        if self.manager:
            self.manager.push_page("snake_game_over")

    def move_snake(self):
        """移动蛇"""
        # 更新方向
        self.direction = self.next_direction

        # 计算新的头部位置
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # 检查碰撞
        if self.check_collision(new_head):
            self.game_over = True
            return

        # 添加新头部
        self.snake.insert(0, new_head)

        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.spawn_food()
            # 加速游戏
            if self.move_interval > 0.05:
                self.move_interval -= 0.005
        else:
            # 移除尾部
            self.snake.pop()

    def check_collision(self, pos):
        """检查碰撞"""
        x, y = pos

        # 检查墙壁碰撞
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return True

        # 检查自身碰撞
        if pos in self.snake:
            return True

        return False

    def render(self, display):
        """绘制游戏画面"""
        super().render(display)

        # 绘制边框（整个屏幕，不填充）
        display.rect(0, 0, 128, 64, 1, False)

        # 绘制蛇
        for i, (x, y) in enumerate(self.snake):
            px = x * self.grid_size
            py = y * self.grid_size

            # 蛇头用填充矩形，身体用空心矩形
            if i == 0:
                display.fill_rect(px, py, self.grid_size, self.grid_size, 1)
            else:
                # 身体用稍小的矩形
                display.fill_rect(
                    px + 1, py + 1, self.grid_size - 2, self.grid_size - 2, 1
                )

        # 绘制食物（闪烁效果）
        if not self.game_over:
            fx, fy = self.food
            px = fx * self.grid_size
            py = fy * self.grid_size

            # 使用时间戳实现闪烁
            if int(time.time() * 1000 / 300) % 2 == 0:
                display.fill_rect(
                    px + 1, py + 1, self.grid_size - 2, self.grid_size - 2, 1
                )
            else:
                display.rect(px, py, self.grid_size, self.grid_size, 1)

        # 显示分数（右上角）
        score_str = f"{self.score}"
        display.text(score_str, 128 - len(score_str) * 8, 0, 1)

    def _handle_page_event(self, event):
        """处理页面事件"""
        event_type = event.get("type")
        key = event.get("key")

        if event_type == "key_press":
            if key == "up":
                self.change_direction((0, -1))
                return True
            elif key == "down":
                self.change_direction((0, 1))
                return True
            elif key == "back":
                # 开始检测长按
                self.back_key_pressed = True
                self.back_key_press_time = 0
                # back 对应向左
                self.change_direction((-1, 0))
                return True
            elif key == "ok":
                # ok 对应向右
                self.change_direction((1, 0))
                return True

        elif event_type == "key_release":
            if key == "back":
                # 重置长按检测
                self.back_key_pressed = False
                self.back_key_press_time = 0
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
        # 如果是从游戏结束页面返回，重置游戏已在返回前处理


class SnakePausePage(Page):
    """贪吃蛇暂停页面"""

    def __init__(self, game_page):
        super().__init__("SnakePause")
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


class SnakeGameOverPage(Page):
    """贪吃蛇游戏结束页面"""

    def __init__(self, game_page):
        super().__init__("SnakeGameOver")
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


# 用于兼容性的别名
SnakeGame = SnakeGamePage
