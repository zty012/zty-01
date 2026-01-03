# UI Pages Directory

本目录包含所有独立的 UI 页面模块。

## 文件结构

```
pages/
├── __init__.py          # 包初始化文件，导出所有页面类
├── main_menu.py         # 主菜单页面
├── clock.py             # 时钟页面
├── network.py           # 网络状态页面
├── system_info.py       # 系统信息页面
├── led_test.py          # LED 测试页面
├── about.py             # 关于页面
├── settings.py          # 设置页面
└── README.md            # 本文件
```

## 页面说明

### main_menu.py - 主菜单
- **类名**: `MainMenu`
- **功能**: 应用程序的主菜单，提供导航到其他页面的入口
- **按键**: 上/下选择，OK 确认

### clock.py - 时钟
- **类名**: `ClockPage`
- **功能**: 实时显示当前时间、日期和星期
- **按键**: Back 返回

### network.py - 网络状态
- **类名**: `NetworkStatusPage`
- **功能**: 显示 WiFi 连接状态、SSID、IP 地址和信号强度
- **按键**: Back 返回
- **特性**: 每 2 秒自动刷新网络信息

### system_info.py - 系统信息
- **类名**: `SystemInfoPage`
- **功能**: 显示 MCU 型号、CPU 频率、可用内存和系统运行时间
- **按键**: Back 返回
- **特性**: 实时更新内存和运行时间

### led_test.py - LED 测试
- **类名**: `LEDTestPage`
- **功能**: 测试和控制 RGB LED 灯
- **按键**: 上/下切换颜色，Back 返回
- **颜色**: Off, Red, Green, Blue, Yellow, Cyan, Magenta, White

### about.py - 关于
- **类名**: `AboutPage`
- **功能**: 显示应用版本信息
- **按键**: Back 返回

### settings.py - 设置
- **类名**: `SettingsPage`
- **功能**: 设置菜单（占位符，待扩展）
- **按键**: 上/下选择，OK 确认，Back 返回

## 使用方法

### 方式 1：导入 pages 子包（推荐）

```python
from ui_app import pages

# 使用页面类
menu = pages.main_menu.MainMenu()
clock = pages.clock.ClockPage()
network = pages.network.NetworkStatusPage()
```

### 方式 2：导入特定子模块

```python
from ui_app.pages import main_menu, clock, network

# 使用页面类
menu = main_menu.MainMenu()
clock_page = clock.ClockPage()
network_page = network.NetworkStatusPage()
```

### 方式 3：直接导入页面类（兼容旧代码）

```python
from ui_app.pages.clock import ClockPage
from ui_app.pages.main_menu import MainMenu

clock = ClockPage()
menu = MainMenu()
```

### 使用 create_ui 函数

```python
from ui_app import create_ui
from ui_framework.framework import UIFramework

ui = UIFramework(display)
create_ui(ui)
```

## 添加新页面

1. 在 `pages/` 目录下创建新的 `.py` 文件
2. 继承 `ui_framework.page.Page` 类
3. 在 `__init__.py` 中导入并添加到 `__all__` 列表
4. 如果需要在主菜单中显示，修改 `main_menu.py`

### 示例：创建新页面

```python
# pages/my_page.py
from ui_framework.component import Text
from ui_framework.page import Page

class MyPage(Page):
    def __init__(self):
        super().__init__("MyPage")
        
        title = Text("My Page", x=64, y=32)
        title.align = "center"
        self.add_component(title)
    
    def _handle_page_event(self, event):
        if event.get("type") == "key_press" and event.get("key") == "back":
            if self.manager:
                self.manager.pop_page()
            return True
        return False
```

然后在 `__init__.py` 中导入子模块（如果还没有）：

```python
from ui_app.pages import (
    # ... 其他模块
    my_page,
)
```

使用时：

```python
from ui_app.pages import my_page

page = my_page.MyPage()
```

## 兼容性

- 原有的 `ui_app/pages.py` 文件保留为兼容层
- 可以通过 `from ui_app.pages.xxx import ClassName` 直接导入页面类
- `create_ui()` 函数仍可从 `ui_app.pages` 或 `ui_app` 导入
- 推荐使用子模块导入方式：`from ui_app.pages import module_name`

## 注意事项

- 每个页面文件只包含一个页面类
- 页面类名应使用 PascalCase 命名
- 文件名应使用 snake_case 命名
- 所有页面都应实现 `_handle_page_event()` 方法处理按键事件
- Back 键通常用于返回上一页面