# 贪吃蛇游戏 🐍

## 文件位置
`src/ui_app/snake_game.py`

## 游戏说明

经典的贪吃蛇游戏，适配 ZTY-01 设备的 128x64 OLED 屏幕。

### 按键操作

**游戏中：**
- `UP` (K3) - 向上移动
- `DOWN` (K4) - 向下移动  
- `BACK` (K1) - 向左移动
- `OK` (K2) - 向右移动
- `长按 BACK` (≥0.5秒) - 暂停游戏

**暂停菜单：**
- `UP/DOWN` - 选择选项
- `OK` - 确认
- `BACK` - 继续游戏（快捷键）

选项：
- Continue - 继续游戏
- Restart - 重新开始
- Exit - 退出到主菜单

**游戏结束菜单：**
- `UP/DOWN` - 选择选项
- `OK` - 确认
- `BACK` - 退出游戏（快捷键）

选项：
- Restart - 重新开始
- Exit - 退出到主菜单

### 游戏规则

- 控制蛇吃食物（闪烁的方块）
- 每吃一个食物 +10 分
- 蛇会越来越长，速度越来越快
- 碰到墙壁或自己的身体 = 游戏结束

## 技术实现

### 页面架构

游戏由三个独立页面组成：

1. **SnakeGamePage** - 主游戏页面
   - 游戏逻辑和渲染
   - 长按检测
   - 状态管理

2. **SnakePausePage** - 暂停页面
   - 使用 Menu 组件
   - 保持游戏状态
   - 提供继续/重新开始/退出选项

3. **SnakeGameOverPage** - 游戏结束页面
   - 显示最终分数
   - 使用 Menu 组件
   - 提供重新开始/退出选项

### 状态保存

- 长按 BACK 键时，游戏状态保存在 `SnakeGamePage` 实例中
- 切换到暂停/游戏结束页面时使用 `push_page`
- 返回时使用 `pop_page`，游戏状态保持不变

### 配置参数

```python
grid_size = 4              # 网格大小：4x4 像素
grid_width = 32            # 32 格宽（128px / 4）
grid_height = 16           # 16 格高（64px / 4）
move_interval = 0.15       # 初始速度：0.15秒/步
long_press_threshold = 0.5 # 长按阈值：0.5秒
```

### 显示效果

- **边框绘制** - 屏幕边缘绘制边框，便于识别游戏区域
- **食物生成** - 食物只在内部区域生成（避开最外层格子），不会紧贴边缘

## 特性

- ✅ 完整的贪吃蛇游戏逻辑
- ✅ 独立的暂停和游戏结束页面
- ✅ 使用 Menu 组件实现菜单
- ✅ 游戏状态自动保存
- ✅ 防止反向移动
- ✅ 食物闪烁效果
- ✅ 动态速度调整（越玩越快）
- ✅ 长按暂停检测
- ✅ 实时分数显示
- ✅ 屏幕边框显示（便于识别边界）
- ✅ 食物避开边缘生成

## 页面注册

在 `pages.py` 中的 `create_ui()` 函数：

```python
snake_game_page = SnakeGamePage()
ui_framework.register_page("snake_game", snake_game_page)
ui_framework.register_page("snake_pause", SnakePausePage(snake_game_page))
ui_framework.register_page("snake_game_over", SnakeGameOverPage(snake_game_page))
```

三个页面共享同一个 `snake_game_page` 实例，确保状态一致。

## 游戏流程

```
主菜单
  │
  ├─> 选择 "Snake Game"
  │
  └─> SnakeGamePage (开始游戏)
        │
        ├─> 长按 BACK ──> SnakePausePage
        │                    │
        │                    ├─> Continue ──> 返回游戏
        │                    ├─> Restart ──> 重置并返回游戏
        │                    └─> Exit ────> 返回主菜单
        │
        └─> 碰撞 ────────> SnakeGameOverPage
                              │
                              ├─> Restart ──> 重新开始游戏
                              └─> Exit ────> 返回主菜单
```



---

**祝你玩得开心！** 🎮