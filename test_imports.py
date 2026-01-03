"""
测试新的包结构导入
验证 ui_framework 和 ui_app 包的导入是否正确
"""

print("=" * 50)
print("测试新的包结构导入")
print("=" * 50)
print()

# 测试 1: 从 ui_framework 包导入
print("测试 1: 从 ui_framework 包导入...")
try:
    from ui_framework import UIFramework

    print("  ✓ from ui_framework import UIFramework")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")

try:
    from ui_framework import Page, PageManager

    print("  ✓ from ui_framework import Page, PageManager")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")

try:
    from ui_framework import Box, Button, Circle, Label, Menu, ProgressBar, Text

    print(
        "  ✓ from ui_framework import Text, Menu, Button, Circle, Label, ProgressBar, Box"
    )
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")

try:
    from ui_framework import InputManager, KeyMapper

    print("  ✓ from ui_framework import InputManager, KeyMapper")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")

print()

# 测试 2: 从子模块直接导入
print("测试 2: 从子模块直接导入...")
try:
    from ui_framework.framework import UIFramework

    print("  ✓ from ui_framework.framework import UIFramework")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")

try:
    from ui_framework.page import Page, PageManager

    print("  ✓ from ui_framework.page import Page, PageManager")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")

try:
    from ui_framework.component import Button, Menu, Text

    print("  ✓ from ui_framework.component import Text, Menu, Button")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")

try:
    from ui_framework.input import InputManager, KeyMapper

    print("  ✓ from ui_framework.input import InputManager, KeyMapper")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")

print()

# 测试 3: 从 ui_app 包导入
print("测试 3: 从 ui_app 包导入...")
try:
    from ui_app import ClockPage, MainMenu, create_ui

    print("  ✓ from ui_app import create_ui, MainMenu, ClockPage")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")

try:
    from ui_app.pages import (
        AboutPage,
        ClockPage,
        LEDTestPage,
        MainMenu,
        NetworkStatusPage,
        SettingsPage,
        SystemInfoPage,
        create_ui,
    )

    print("  ✓ from ui_app.pages import (各种页面类)")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")

print()

# 测试 4: 验证类和对象
print("测试 4: 验证类和对象...")
try:
    from ui_framework import Page, Text, UIFramework

    # 检查是否为类
    assert isinstance(UIFramework, type), "UIFramework 不是类"
    assert isinstance(Page, type), "Page 不是类"
    assert isinstance(Text, type), "Text 不是类"

    print("  ✓ 所有导入的都是有效的类")
except Exception as e:
    print(f"  ✗ 验证失败: {e}")

print()
print("=" * 50)
print("导入测试完成！")
print("=" * 50)
