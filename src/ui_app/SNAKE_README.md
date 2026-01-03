# 贪吃蛇游戏 🐍

## 概述

这是一个为 ZTY-01 设备设计的贪吃蛇游戏，使用 UI 框架实现，包含三个独立页面：
- **游戏主页面** (`SnakeGamePage`)
- **暂停页面** (`SnakePausePage`)
- **游戏结束页面** (`SnakeGameOverPage`)

## 按键说明

### 游戏中
- **UP (K3)** - 向上移动
- **DOWN (K4)** - 向下移动
- **BACK (K1)** - 向左移动
- **OK (K2)** - 向右移动
- **长按 BACK (≥0.5秒)** - 暂停游戏（进入暂停页面）

### 暂停页面
使用 Menu 组件，提供以下选项：
- **Continue** - 继续游戏
- **Restart** - 重新开始
- **Exit** - 退出游戏

按键操作：
- **UP/DOWN** - 选择菜单项
- **OK** - 确认选择
- **BACK** - 继续游戏（快捷键）

### 游戏结束页面
显示最终分数，使用 Menu 组件提供选项：
- **Restart** - 重新开始
- **Exit** - 退出游戏

按键操作：
- **UP/DOWN** - 选择菜单项
- **OK** - 确认选择
- **BACK** - 退出游戏（快捷键）

## 游戏规则

1. 控制蛇吃食物（闪烁的方块）来增加分数
2. 每吃一个食物得 **10 分**
3. 蛇会随着吃食物而变长
4. 碰到墙壁或自己的身体则游戏结束
5. 游戏速度会随分数增加而逐渐加快

## 技术实现

### 页面架构

```
MainMenu
    └─> SnakeGamePage (游戏主页面)
            ├─> SnakePausePage (暂停页面)
            └─> SnakeGameOverPage (游戏结束页面)
```

### 游戏状态保存

- 长按 BACK 键时，游戏状态自动保存在 `SnakeGamePage` 实例中
- 切换到暂停页面时，游戏画面保持不变
- 从暂停页面返回时，游戏继续运行

### 核心参数

```python
grid_size = 4           # 网格大小（像素）
grid_width = 32         # 网格宽度（32格）
grid_height = 16        # 网格高度（16格）
move_interval = 0.15    # 初始移动间隔（秒）
long_press_threshold = 0.5  # 长按阈值（秒）
```

### 类说明

#### SnakeGamePage
主游戏页面，负责：
- 游戏逻辑（蛇移动、碰撞检测、食物生成）
- 游戏渲染（绘制蛇、食物、分数）
- 按键处理（方向控制、长按检测）
- 页面切换（暂停、游戏结束）

#### SnakePausePage
暂停页面，负责：
- 显示暂停菜单
- 处理继续/重新开始/退出操作
- 维持游戏状态（不更新游戏逻辑）

#### SnakeGameOverPage
游戏结束页面，负责：
- 显示最终分数
- 显示游戏结束菜单
- 处理重新开始/退出操作

## 页面注册

在 `pages.py` 中的 `create_ui()` 函数中注册三个页面：

```python
snake_game_page = SnakeGamePage()
ui_framework.register_page("snake_game", snake_game_page)
ui_framework.register_page("snake_pause", SnakePausePage(snake_game_page))
ui_framework.register_page("snake_game_over", SnakeGameOverPage(snake_game_page))
```

## 游戏流程

1. 从主菜单选择 "Snake Game"
2. 进入游戏主页面，开始游戏
3. 长按 BACK 键 → 进入暂停页面
   - 选择 Continue → 返回游戏
   - 选择 Restart → 重置游戏并返回
   - 选择 Exit → 退出到主菜单
4. 游戏结束 → 自动进入游戏结束页面
   - 显示最终分数
   - 选择 Restart → 重新开始游戏
   - 选择 Exit → 退出到主菜单

## 特性

- ✅ 完整的游戏逻辑
- ✅ 独立的暂停和游戏结束页面
- ✅ 使用 Menu 组件实现菜单
- ✅ 游戏状态保存
- ✅ 防止反向移动
- ✅ 食物闪烁效果
- ✅ 动态速度调整
- ✅ 长按检测
- ✅ 实时分数显示

## 扩展建议

1. **保存最高分** - 使用 config 模块保存历史最高分
2. **难度选择** - 添加难度设置页面
3. **音效** - 添加吃食物和游戏结束的提示音
4. **障碍物模式** - 随机生成障碍物
5. **不同食物** - 不同颜色的食物有不同效果

## 配置调整

修改 `SnakeGamePage.__init__()` 中的参数：

- `self.grid_size` - 调整网格大小
- `self.move_interval` - 调整初始速度
- `self.long_press_threshold` - 调整长按时间

## 注意事项

- 游戏状态保存在 `SnakeGamePage` 实例中
- 暂停和游戏结束页面共享同一个游戏实例
- 页面切换使用 `push_page` 和 `pop_page`
- 从暂停页面"Exit"会连续 pop 两次（退出暂停页面和游戏页面）