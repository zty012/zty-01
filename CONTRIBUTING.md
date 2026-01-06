# 开发指南

## 环境要求

- 推荐使用 Arch Linux，因为本项目用到的依赖都在它的官方源里
- Zed（VS Code 也可以，但需要自行配置 MicroPython 的类型提示）
- Python 3.13
- uv
- mpremote（可选，如果不需要使用 REPL 调试可以不安装）

## 安装依赖

这也是以下所有命令的前提。

```sh
uv sync
```

## 构建字体文件（`unifont.bin` 和 `unifont_chars.txt`）

仓库中已经包含了预构建的字体文件（仅包含 ASCII 和 GB2312 中的字符），但如果你需要包含其他字符，可以按照以下步骤重新构建字体文件：

1. [下载](https://github.com/multitheftauto/unifont/releases) TTF 格式的字体文件，重命名为 `unifont.ttf`，移动到项目根目录下。
2. 准备字符集文件：
   - 如果你只需要 ASCII 和 GB2312 字符，可以直接使用仓库中的 `chars.txt`。
   - 如果需要其他字符，可以修改并运行 `./scripts/generate_char_list.py` 脚本生成字符集文件。
3. 确保项目根目录下有 `unifont.ttf` 和 `chars.txt` 文件。
4. 运行 `./scripts/generate_font_bin.py` 脚本生成 `unifont.bin` 文件。
5. 将生成的 `unifont.bin` 和之前生成的 `chars.txt` 移动到 `src/assets/` 目录下，替换原有文件。
