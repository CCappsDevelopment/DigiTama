
# demo_bg_image.py
# Overlay static menu.raw on animated water_XX.raw frames using a colorkey.

import time

FRAME_FILES = [f"water_{i:02d}.raw" for i in range(20)]
FRAME_DELAY = 0.08  # adjust as desired

WIDTH  = 128
HEIGHT = 128
PIXELS = WIDTH * HEIGHT
BYTES_PER_PIXEL = 2
BUF_SIZE = PIXELS * BYTES_PER_PIXEL

# RGB565 magenta (255,0,255) as transparency key
TRANSPARENT_KEY = 0xF81F  # r=31,g=0,b=31 in 5-6-5


def load_raw(path):
    with open(path, "rb") as f:
        data = f.read()
    if len(data) != BUF_SIZE:
        raise ValueError("Unexpected size for %s: %d" % (path, len(data)))
    return bytearray(data)  # mutable for compositing


def run(display, btn_a=None, btn_b=None):
    # Load static menu once
    menu_buf = load_raw("menutest.raw")

    while True:
        for fname in FRAME_FILES:
            # 1. Load background frame
            bg = load_raw(fname)

            # 2. Composite menu using colorkey
            # Walk 16-bit words; i indexes bytes
            i = 0
            while i < BUF_SIZE:
                # menu pixel
                hi = menu_buf[i]
                lo = menu_buf[i + 1]
                color = (hi << 8) | lo
                if color != TRANSPARENT_KEY:
                    # overwrite background pixel
                    bg[i]     = hi
                    bg[i + 1] = lo
                i += 2

            # 3. Blit combined buffer
            display.block(0, 0, WIDTH - 1, HEIGHT - 1, bg)
            time.sleep(FRAME_DELAY)

