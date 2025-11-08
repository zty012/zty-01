# 开发指南

## 准备

本项目需要一块 `ESP32-S3-DevKitC-1` 开发板。

电脑上需要安装以下软件：

- `esptool` 用于刷写 MicroPython 固件，以及清空内部存储空间
- `mpremote` 用于将代码上传到开发板，以及进入 REPL 模式
- Zed 或 VSCode 编辑器，用于编写代码

然后将开发板的 `COM` 接口通过数据线连接到电脑，并进行以下步骤：

### 如果使用 Windows，可能需要安装驱动

如果连接开发板后，设备管理器中没有出现开发板串口，需要安装驱动，有关驱动安装请自行探索。

### 如果使用 Linux，需要配置串口权限 (udev 规则)

首先使用 `lsusb` 查看 USB 设备的 Vendor ID 和 Product ID，例如：

```
Bus 001 Device 007: ID 1a86:55d3 QinHeng Electronics USB Single Serial
```

然后创建一个 udev 规则文件 `/etc/udev/rules.d/99-esp32.rules`，内容如下：

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", MODE="0666"
```

然后重新加载 udev 规则：

```sh
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## 刷入 MicroPython 固件

从 [MicroPython 官网](https://micropython.org/download/ESP32_GENERIC_S3/) 下载最新版本的固件 `ESP32_GENERIC_S3-xxxxxxxx-vx.xx.x.bin`

先清空开发板的存储空间：

```sh
esptool erase_flash
```

然后刷入 MicroPython 固件：

```sh
esptool --baud 460800 write_flash 0 <固件文件路径>
```

## (可选) 配置类型提示

需要安装 `uv` 工具。

运行 `uv install` 即可，目前只支持 Zed，详情请见[《给 MicroPython 的模块添加类型提示，提升开发体验》](https://2y.nz/p/mpy-types/)

## 上传代码

使用 `mpremote` 脚本上传代码：

```sh
mpremote cp -r ./src/. :
```
