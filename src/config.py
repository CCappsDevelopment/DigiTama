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
# SPRITE SHEET
# =============================================================================
SPRITE_W = 16
SPRITE_H = 16
SPRITE_SHEET_W = 48
SPRITE_SHEET_H = 64
SPRITE_FRAMES_PER_ROW = 3
SPRITE_ROWS = 4  # forward, left, right, back

# Sprite position (centered)
SPRITE_X = (WIDTH - SPRITE_W) // 2
SPRITE_Y = (HEIGHT - SPRITE_H) // 2

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
ASSET_MENU = "menutest.raw"
ASSET_SPRITE = "lilguy.raw"
ASSET_BG_FRAMES = [f"water_{i:02d}.raw" for i in range(20)]
