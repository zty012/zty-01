from machine import I2C, Pin

import ssd1306
from led import set_led_color

set_led_color(2, 5, 16)

scl = Pin(16)
sda = Pin(15)
i2c = I2C(scl=scl, sda=sda)
display = ssd1306.SSD1306_I2C(128, 64, i2c)

display.fill(0)
display.text("Booting...", 0, 0)
display.show()
