from ui_app.pages.about import AboutPage
from ui_app.pages.flappy_bird import FlappyBirdPage
from ui_app.pages.home import Home
from ui_app.pages.led_page import LEDPage
from ui_app.pages.lessons import LessonsPage
from ui_app.pages.main_menu import MainMenu
from ui_app.pages.network import NetworkPage
from ui_app.pages.settings import SettingsPage
from ui_app.pages.snake_game import SnakeGamePage


def create_ui(ui_framework):
    """
    创建实用 UI 页面

    Args:
        ui_framework: UIFramework 实例
    """

    # 注册所有实用页面
    ui_framework.register_page("home", Home())
    ui_framework.register_page("main_menu", MainMenu())
    ui_framework.register_page("snake_game", SnakeGamePage())
    ui_framework.register_page("flappy_bird", FlappyBirdPage())
    ui_framework.register_page("network", NetworkPage())
    ui_framework.register_page("led", LEDPage())
    ui_framework.register_page("lessons", LessonsPage())
    ui_framework.register_page("about", AboutPage())
    ui_framework.register_page("settings", SettingsPage())

    # 设置首页
    ui_framework.goto_page("home", clear_stack=True)
