# config.py
# Central configuration for DigiTama virtual pet

# =============================================================================
# DISPLAY
# =============================================================================
WIDTH = 128
HEIGHT = 128
BPP = 2  # Bytes per pixel (RGB565)
BUF_SIZE = WIDTH * HEIGHT * BPP  # 32768 bytes

# =============================================================================
# SPI / OLED PINS
# =============================================================================
SPI_ID = 0
PIN_SCK = 2    # GP2 -> SCK
PIN_MOSI = 3   # GP3 -> MOSI
PIN_MISO = 4   # GP4 -> (unused by OLED)
PIN_CS = 5     # GP5 -> TCS (chip select)
PIN_DC = 6     # GP6 -> DC (data/command)
PIN_RST = 7    # GP7 -> RST (reset)

SPI_BAUDRATE = 16_000_000
SPI_POLARITY = 0
SPI_PHASE = 0

# =============================================================================
# BUTTONS (active-low with internal pull-up)
# =============================================================================
PIN_BTN_A = 10  # GP10 -> Next
PIN_BTN_B = 11  # GP11 -> Confirm
PIN_BTN_C = 12  # GP12 -> Back/Cancel

# =============================================================================
# TIMING
# =============================================================================
SCREEN_TIMEOUT_MS = 20_000       # Screen sleep after 20s inactivity
GAME_TICK_MS = 600               # Game logic tick (600ms, OSRS-inspired)
BG_FRAME_DELAY_MS = 80           # Background animation speed (~12.5 FPS)
SPRITE_FPS = 3                   # Sprite animation speed
SPRITE_FRAME_DELAY_MS = int(1000 / SPRITE_FPS)
INPUT_POLL_MS = 5                # Button polling interval (fast for responsiveness)
DEBOUNCE_MS = 100                # Button debounce time (filters press/release bounce)

# =============================================================================
# SPRITE SHEET (yoshisprite.raw: 320x96, 32x32 frames)
# =============================================================================
SPRITE_W = 32
SPRITE_H = 32
SPRITE_SHEET_W = 320
SPRITE_SHEET_H = 96

# Animation definitions: (row_y, frame_count)
# Row 0 (Y: 0-31): Walk - 10 frames
# Row 1 (Y: 32-63): Idle-Trot - 8 frames
# Row 2 (Y: 64-95): Idle-Chin Scratch - 8 frames
ANIM_WALK = 0
ANIM_IDLE_TROT = 1
ANIM_CHIN_SCRATCH = 2

ANIM_FRAME_COUNTS = {
    ANIM_WALK: 10,
    ANIM_IDLE_TROT: 8,
    ANIM_CHIN_SCRATCH: 8,
}

# Current animation to play
CURRENT_ANIM = ANIM_IDLE_TROT
SPRITE_FRAMES_PER_ROW = ANIM_FRAME_COUNTS[CURRENT_ANIM]
SPRITE_ROWS = 3  # walk, idle-trot, chin-scratch

# Sprite scaling (render size = SPRITE_W * SPRITE_SCALE)
SPRITE_SCALE = 2  # 32x32 sprite rendered as 64x64
SPRITE_DISPLAY_W = SPRITE_W * SPRITE_SCALE
SPRITE_DISPLAY_H = SPRITE_H * SPRITE_SCALE

# Sprite position (centered based on display size)
SPRITE_X = (WIDTH - SPRITE_DISPLAY_W) // 2
SPRITE_Y = (HEIGHT - SPRITE_DISPLAY_H) // 2

# =============================================================================
# COLORS (RGB565)
# =============================================================================
def color565(r, g, b):
    """Convert 8-bit RGB to RGB565."""
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | (b >> 3)

BLACK = color565(0, 0, 0)
WHITE = color565(255, 255, 255)
TRANSPARENT_KEY = color565(255, 0, 255)  # Magenta #FF00FF

# =============================================================================
# MENU LAYOUT
# =============================================================================
# 10 menu entries: 5 top bar, 5 bottom bar
# Each tuple: (x0, y0, x1, y1) inclusive bounds
MENU_RECTS = [
    (  1,   1,  24,  14),  # 0 - top bar
    ( 27,   1,  50,  14),  # 1
    ( 52,   1,  75,  14),  # 2
    ( 77,   1, 100,  14),  # 3
    (103,   1, 126,  14),  # 4
    (  1, 113,  24, 126),  # 5 - bottom bar
    ( 27, 113,  50, 126),  # 6
    ( 52, 113,  75, 126),  # 7
    ( 77, 113, 100, 126),  # 8
    (103, 113, 126, 126),  # 9
]

# =============================================================================
# ASSET PATHS
# =============================================================================
ASSET_BG = "tree-bg.raw"
ASSET_MENU = "menutest.raw"  # Menu overlay with transparency
ASSET_SPRITE = "yoshisprite.raw"
