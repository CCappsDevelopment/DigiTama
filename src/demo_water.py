# demo_water.py
# Stream water_00.raw .. water_19.raw from flash, one frame at a time.

import time

FRAMES = [f"water_{i:02d}.raw" for i in range(20)]
FRAME_DELAY = 0.08  # seconds per frame (~12.5 FPS)

def show_frame(display, filename):
    with open(filename, "rb") as f:
        buf = f.read()
    w = display.width
    h = display.height
    display.block(0, 0, w - 1, h - 1, buf)

def run(display, btn_a=None, btn_b=None):
    while True:
        for name in FRAMES:
            show_frame(display, name)
            time.sleep(FRAME_DELAY)


