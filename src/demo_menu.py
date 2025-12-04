# demo_menu.py
# Water animation + static menu (menutest.raw) + invert highlight.

import time

FRAME_FILES = [f"water_{i:02d}.raw" for i in range(20)]
FRAME_DELAY = 0.08

WIDTH  = 128
HEIGHT = 128
BPP    = 2
PIXELS = WIDTH * HEIGHT
BUF_SIZE = PIXELS * BPP

# RGB565 colorkey for transparency (magenta #FF00FF)
def color565(r, g, b):
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | (b >> 3)

TRANSPARENT_KEY = color565(255, 0, 255)

# Menu entry rectangles: (x0, y0, x1, y1)
MENU_RECTS = [
    (  1,  1,  24,  14),  # 0
    ( 27,  1,  50,  14),  # 1
    ( 52,  1,  75,  14),  # 2
    ( 77,  1, 100,  14),  # 3
    (103,  1, 126,  14),  # 4
    (  1,113,  24, 126),  # 5
    ( 27,113,  50, 126),  # 6
    ( 52,113,  75, 126),  # 7
    ( 77,113, 100, 126),  # 8
    (103,113, 126, 126),  # 9
]


def load_raw(path):
    with open(path, "rb") as f:
        data = f.read()
    if len(data) != BUF_SIZE:
        raise ValueError("Unexpected size for %s: %d" % (path, len(data)))
    return bytearray(data)


def overlay_menu(bg_buf, menu_buf):
    """Apply menu layer with colorkey onto bg_buf in-place."""
    i = 0
    while i < BUF_SIZE:
        hi = menu_buf[i]
        lo = menu_buf[i + 1]
        color = (hi << 8) | lo
        if color != TRANSPARENT_KEY:
            bg_buf[i]     = hi
            bg_buf[i + 1] = lo
        i += 2


def invert_rect(buf, rect):
    """Invert colors in a rectangle (in-place) on an RGB565 buffer."""
    x0, y0, x1, y1 = rect
    if x0 < 0: x0 = 0
    if y0 < 0: y0 = 0
    if x1 >= WIDTH:  x1 = WIDTH - 1
    if y1 >= HEIGHT: y1 = HEIGHT - 1

    for y in range(y0, y1 + 1):
        row_start = (y * WIDTH + x0) * BPP
        for x in range(x0, x1 + 1):
            i = row_start + (x - x0) * BPP
            hi = buf[i]
            lo = buf[i + 1]
            c  = (hi << 8) | lo
            c ^= 0xFFFF
            buf[i]     = (c >> 8) & 0xFF
            buf[i + 1] = c & 0xFF


def run(display, btn_a, btn_b=None, btn_c=None):
    # Load static menu once
    menu_buf = load_raw("menutest.raw")

    selected = None
    last_a = btn_a.value() if btn_a else 1
    last_c = btn_c.value() if btn_c else 1

    while True:
        for fname in FRAME_FILES:
            # 1. Background frame
            frame = load_raw(fname)

            # 2. Overlay menu graphic (solid pixels from menutest.raw)
            overlay_menu(frame, menu_buf)

            # 3. Apply selection highlight if any
            if selected is not None:
                invert_rect(frame, MENU_RECTS[selected])

            # 4. Draw to display
            display.block(0, 0, WIDTH - 1, HEIGHT - 1, frame)

            # 5. Handle buttons
            if btn_a:
                va = btn_a.value()
                if last_a == 1 and va == 0:  # rising edge: A pressed
                    if selected is None:
                        selected = 0
                    else:
                        selected = (selected + 1) % len(MENU_RECTS)
                    print("Selected menu entry:", selected)
                last_a = va

            if btn_c:
                vc = btn_c.value()
                if last_c == 1 and vc == 0:  # C pressed
                    selected = None
                    print("Selection cleared")
                last_c = vc

            time.sleep(FRAME_DELAY)

