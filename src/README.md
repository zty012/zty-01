# ZTY-01 源代码目录

## 📁 目录结构

```
src/
├── ui_framework/          # UI 框架核心库（可复用）
│   ├── __init__.py       # 包导出
│   ├── framework.py      # UIFramework 主类
│   ├── page.py           # Page, PageManager
│   ├── component.py      # UI 组件（Text, Menu, Button 等）
│   └── input.py          # InputManager, KeyMapper
│
├── ui_app/               # UI 应用实现（具体页面）
│   ├── __init__.py       # 包导出
│   ├── pages.py          # 实用页面（时钟、网络、系统信息等）
│   └── main_ui.py        # 集成示例
│
├── __init__.py           # 包初始化（版本信息）
├── boot.py               # 启动脚本
├── main.py               # 主程序入口
├── config.py             # 配置管理
├── led.py                # LED 控制
├── ntp.py                # NTP 时间同步
├── ssd1306.py            # OLED 显示驱动
├── bh1750.py             # 光传感器驱动
└── easings.py            # 缓动函数
```

## 🎨 UI 框架（ui_framework/）

UI 框架是可复用的核心库，提供完整的 UI 开发能力。

### 主要组件

- **UIFramework** - UI 框架主类，整合所有功能
- **Page / PageManager** - 页面管理，支持页面栈导航
- **Component** - 组件系统：Text, Menu, Button, Circle, ProgressBar 等
- **InputManager** - 输入管理，支持按键防抖和长按检测

### 导入方式

```python
# 方式 1：从包导入（推荐）
from ui_framework import UIFramework, Page, Text, Menu

# 方式 2：从子模块导入
from ui_framework.framework import UIFramework
from ui_framework.page import Page
from ui_framework.component import Text, Menu
```

## 📱 UI 应用（ui_app/）

基于 UI 框架实现的具体应用页面。

### 预定义页面

- **MainMenu** - 主菜单页面
- **ClockPage** - 时钟显示
- **NetworkStatusPage** - 网络状态
- **SystemInfoPage** - 系统信息
- **LEDTestPage** - LED 测试
- **AboutPage** - 关于页面
- **SettingsPage** - 设置页面

### 使用方式

```python
from ui_framework import UIFramework
from ui_app import create_ui

# 创建框架并加载所有预定义页面
ui = UIFramework(display)
create_ui(ui)
ui.run()
```

## 🔧 工具模块

### config.py - 配置管理
```python
from config import config

# 获取配置
wifi_ssid = config.get("wifi", {}).get("ssid")

# 设置配置
config.set("key", "value")
config.save()
```

### led.py - LED 控制
```python
from led import set_led_color

# 设置 RGB LED 颜色
set_led_color(r=16, g=0, b=0)  # 红色
```

### ntp.py - NTP 时间同步
```python
from ntp import Ntp

Ntp.set_hosts(["pool.ntp.org"])
Ntp.set_timezone(8, 0)  # UTC+8
Ntp.rtc_sync()
```

## 📝 导入规则

### ✅ 正确的导入方式

```python
# 绝对导入（相对于 src/ 目录）
from ui_framework import UIFramework
from ui_app import create_ui
from config import config
from led import set_led_color
```

### ❌ 错误的导入方式

```python
# 不要使用相对导入
from .ui_framework import UIFramework  # 错误
from ..config import config            # 错误
```

## 🚀 快速开始

### 最小示例

```python
from machine import I2C, Pin
import ssd1306
from ui_framework import UIFramework, Page, Text

# 初始化显示
i2c = I2C(scl=Pin(16), sda=Pin(15))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# 创建简单页面
class HelloPage(Page):
    def __init__(self):
        super().__init__("Hello")
        text = Text("Hello World!", x=64, y=32)
        text.align = "center"
        self.add_component(text)

# 创建 UI 并运行
ui = UIFramework(display)
ui.register_page("hello", HelloPage())
ui.goto_page("hello")
ui.run()
```

### 完整示例（使用预定义页面）

参考 `main.py` 查看完整的集成示例。

## 📚 相关文档

- **[../NEW_IMPORT_GUIDE.md](../NEW_IMPORT_GUIDE.md)** - 导入指南（必读）
- **[../PACKAGE_STRUCTURE.md](../PACKAGE_STRUCTURE.md)** - 包结构说明
- **[../UI_FRAMEWORK_README.md](../UI_FRAMEWORK_README.md)** - UI 框架文档
- **[../DIRECTORY_TREE.md](../DIRECTORY_TREE.md)** - 完整目录结构

## 💡 设计原则

1. **分层架构** - 应用层、框架层、驱动层、硬件层
2. **模块化** - ui_framework 可独立复用
3. **绝对导入** - 所有导入相对于 src/ 目录
4. **单一职责** - 每个模块专注于特定功能

## 🎯 主程序入口

运行主程序：

```bash
python main.py
```

主程序会：
1. 连接 WiFi
2. 同步时间
3. 初始化显示
4. 创建 UI 框架
5. 注册按钮
6. 加载所有页面
7. 启动 UI 主循环

---

**版本**: 2.0（重构后）  
**Python**: MicroPython  
**硬件**: ESP32-S3