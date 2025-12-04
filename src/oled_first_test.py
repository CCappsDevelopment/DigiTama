from machine import Pin, SPI
import time
import ssd1351

# SPI setup
spi = SPI(
    0,
    baudrate=16_000_000,   # you can lower to 1_000_000 if needed
    polarity=0,
    phase=0,
    sck=Pin(2),            # GP2 -> SCK
    mosi=Pin(3),           # GP3 -> MOSI
    miso=Pin(4)            # unused by display
)

cs  = Pin(5, Pin.OUT)      # GP5 -> CS
dc  = Pin(6, Pin.OUT)      # GP6 -> DC
rst = Pin(7, Pin.OUT)      # GP7 -> RST

# Create display object (this will reset and init the panel)
display = ssd1351.Display(spi, cs, dc, rst, width=128, height=128)

# Helper: convert 0–255 RGB to RGB565 used by the display
def color565(r, g, b):
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | (b >> 3)

# Fill entire screen red
RED = color565(255, 0, 0)
display.clear(RED)

# Draw a small green square in the corner
GREEN = color565(0, 255, 0)
for x in range(10, 30):
    for y in range(10, 30):
        display.draw_pixel(x, y, GREEN)

# You’re done; no display.show() needed for this driver
while True:
    time.sleep(1)

