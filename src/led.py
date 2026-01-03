import time

import neopixel
from machine import Pin

from easings import ease_out_expo

pin = Pin(48, Pin.OUT)
np = neopixel.NeoPixel(pin, 1)
np[0] = (0, 0, 0)
np.write()


def set_led_color(r: int, g: int, b: int, duration: float = 0.25, easing=ease_out_expo):
    """设置LED颜色，支持缓动效果

    Args:
        r, g, b: 目标RGB值 (0-255)
        duration: 过渡时间（秒）
        easing: 缓动函数，默认为 ease_out_expo
    """

    sr, sg, sb = np[0]

    if duration <= 0:
        np[0] = (r, g, b)
        np.write()
        return

    steps = int(duration / 0.02)
    for step in range(1, steps + 1):
        # 计算缓动进度 (0.0 - 1.0)
        progress = easing(step / steps)

        nr = int(sr + (r - sr) * progress)
        ng = int(sg + (g - sg) * progress)
        nb = int(sb + (b - sb) * progress)

        np[0] = (nr, ng, nb)
        np.write()
        time.sleep(0.02)
