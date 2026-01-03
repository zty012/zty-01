from ui_app.pages.about import AboutPage
from ui_app.pages.clock import ClockPage
from ui_app.pages.led_page import LEDPage
from ui_app.pages.main_menu import MainMenu
from ui_app.pages.network import NetworkPage
from ui_app.pages.settings import SettingsPage
from ui_app.pages.system_info import SystemInfoPage
from ui_app.snake_game import SnakeGamePage


def create_ui(ui_framework):
    """
    创建实用 UI 页面

    Args:
        ui_framework: UIFramework 实例
    """

    # 注册所有实用页面
    ui_framework.register_page("main_menu", MainMenu())
    ui_framework.register_page("snake_game", SnakeGamePage())
    ui_framework.register_page("clock", ClockPage())
    ui_framework.register_page("network", NetworkPage())
    ui_framework.register_page("system", SystemInfoPage())
    ui_framework.register_page("led", LEDPage())
    ui_framework.register_page("about", AboutPage())
    ui_framework.register_page("settings", SettingsPage())

    # 设置主菜单为首页
    ui_framework.goto_page("main_menu", clear_stack=True)
