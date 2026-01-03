from ui_app.pages.about import AboutPage
from ui_app.pages.clock import ClockPage
from ui_app.pages.led_test import LEDTestPage
from ui_app.pages.main_menu import MainMenu
from ui_app.pages.network import NetworkStatusPage
from ui_app.pages.settings import SettingsPage
from ui_app.pages.system_info import SystemInfoPage


def create_ui(ui_framework):
    """
    创建实用 UI 页面

    Args:
        ui_framework: UIFramework 实例
    """
    # 导入贪吃蛇游戏
    from ui_app.snake_game import SnakeGameOverPage, SnakeGamePage, SnakePausePage

    # 注册所有实用页面
    ui_framework.register_page("main_menu", MainMenu())

    # 注册贪吃蛇游戏页面
    snake_game_page = SnakeGamePage()
    ui_framework.register_page("snake_game", snake_game_page)
    ui_framework.register_page("snake_pause", SnakePausePage(snake_game_page))
    ui_framework.register_page("snake_game_over", SnakeGameOverPage(snake_game_page))

    ui_framework.register_page("clock", ClockPage())
    ui_framework.register_page("network", NetworkStatusPage())
    ui_framework.register_page("system", SystemInfoPage())
    ui_framework.register_page("led_test", LEDTestPage())
    ui_framework.register_page("about", AboutPage())
    ui_framework.register_page("settings", SettingsPage())

    # 设置主菜单为首页
    ui_framework.goto_page("main_menu", clear_stack=True)
