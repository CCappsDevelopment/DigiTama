# demo_sprite.py
# Water animation + static menu (menutest.raw) + invert highlight + sprite sheet (lilguy.raw).

import time
from screen_sleep import ScreenSleepManager

FRAME_FILES = [f"water_{i:02d}.raw" for i in range(20)]
BG_FRAME_DELAY = 0.08   # water loop speed

WIDTH  = 128
HEIGHT = 128
BPP    = 2
PIXELS = WIDTH * HEIGHT
BUF_SIZE = PIXELS * BPP

# Sprite sheet: 48x64, 16x16 frames, 3 cols x 4 rows
SPRITE_W = 16
SPRITE_H = 16
SPRITE_SHEET_W = 48
SPRITE_SHEET_H = 64

# Sprite animation: 3 frames per row, 4 rows (forward, left, right, back)
SPRITE_FRAMES_PER_ROW = 3
SPRITE_ROWS           = 4

# Center position for sprite on screen
SPRITE_X = (WIDTH  - SPRITE_W) // 2
SPRITE_Y = (HEIGHT - SPRITE_H) // 2

# 3 FPS for sprite => ~0.333s per frame
SPRITE_FRAME_DELAY = 1.0 / 3.0

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


def load_raw(path, expected_size):
    with open(path, "rb") as f:
        data = f.read()
    if len(data) != expected_size:
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


def blit_sprite(frame_buf, sheet_buf, anim_row, frame_index):
    """Blit one 16x16 sprite frame from sheet_buf into frame_buf at SPRITE_X/Y."""
    # Source rect in sheet
    sx0 = SPRITE_W * frame_index
    sy0 = SPRITE_H * anim_row

    for dy in range(SPRITE_H):
        sy = sy0 + dy
        # index into sheet (48-wide)
        sheet_row_start = (sy * SPRITE_SHEET_W + sx0) * BPP

        # index into screen buffer (128-wide)
        dst_y = SPRITE_Y + dy
        frame_row_start = (dst_y * WIDTH + SPRITE_X) * BPP

        for dx in range(SPRITE_W):
            si = sheet_row_start + dx * BPP
            hi = sheet_buf[si]
            lo = sheet_buf[si + 1]
            color = (hi << 8) | lo
            if color == TRANSPARENT_KEY:
                continue  # don't overwrite background/menu
            di = frame_row_start + dx * BPP
            frame_buf[di]     = hi
            frame_buf[di + 1] = lo


def run(display, btn_a, btn_b=None, btn_c=None):
    # Load static assets once
    menu_buf   = load_raw("menutest.raw", BUF_SIZE)
    sprite_buf = load_raw("lilguy.raw", SPRITE_SHEET_W * SPRITE_SHEET_H * BPP)

    # Screen sleep manager (60 second timeout)
    sleep_mgr = ScreenSleepManager(display, [btn_a, btn_b, btn_c], timeout_ms=20_000)

    selected = None
    last_a = btn_a.value() if btn_a else 1
    last_b = btn_b.value() if btn_b else 1
    last_c = btn_c.value() if btn_c else 1

    # Sprite animation state
    anim_row    = 0   # 0=forward, 1=left, 2=right, 3=back
    frame_index = 0   # 0..2
    last_sprite_time = time.ticks_ms()
    
    # Track which background frame we're on
    bg_frame_idx = 0

    while True:
        # Check screen sleep state first
        screen_on, just_woke = sleep_mgr.update()
        
        if not screen_on:
            # Screen is off - sleep briefly and skip rendering
            time.sleep(0.05)
            continue
        
        if just_woke:
            # Screen just woke up - consume the button press, don't act on it
            last_a = btn_a.value() if btn_a else 1
            last_b = btn_b.value() if btn_b else 1
            last_c = btn_c.value() if btn_c else 1

        # Get current background frame
        fname = FRAME_FILES[bg_frame_idx]
        bg_frame_idx = (bg_frame_idx + 1) % len(FRAME_FILES)
        
        # 1. Background frame
        frame = load_raw(fname, BUF_SIZE)

        # 2. Overlay menu
        overlay_menu(frame, menu_buf)

        # 3. Apply menu selection highlight
        if selected is not None:
            invert_rect(frame, MENU_RECTS[selected])

        # 4. Advance sprite frame at 3 FPS
        now = time.ticks_ms()
        if time.ticks_diff(now, last_sprite_time) >= int(SPRITE_FRAME_DELAY * 1000):
            last_sprite_time = now
            frame_index = (frame_index + 1) % SPRITE_FRAMES_PER_ROW

        # 5. Blit current sprite frame
        blit_sprite(frame, sprite_buf, anim_row, frame_index)

        # 6. Draw to display
        display.block(0, 0, WIDTH - 1, HEIGHT - 1, frame)

        # 7. Handle buttons

        # BTN A: menu selection advance (same as before)
        if btn_a:
            va = btn_a.value()
            if last_a == 1 and va == 0:
                if selected is None:
                    selected = 0
                else:
                    selected = (selected + 1) % len(MENU_RECTS)
                print("Selected menu entry:", selected)
            last_a = va

        # BTN B: cycle sprite animation row
        if btn_b:
            vb = btn_b.value()
            if last_b == 1 and vb == 0:
                anim_row = (anim_row + 1) % SPRITE_ROWS
                print("Sprite anim row:", anim_row)
            last_b = vb

        # BTN C: clear selection
        if btn_c:
            vc = btn_c.value()
            if last_c == 1 and vc == 0:
                selected = None
                print("Selection cleared")
            last_c = vc

        time.sleep(BG_FRAME_DELAY)

