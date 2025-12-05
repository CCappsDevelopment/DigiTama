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
# GAME PHASES (lifecycle state machine)
# =============================================================================
PHASE_WAITING = 0    # Initial state: no pet, waiting for BTN A + BTN C to start
PHASE_EGG = 1        # Egg displayed, hatching countdown active
PHASE_ALIVE = 2      # DigiTama alive, normal gameplay
PHASE_DEAD = 3       # Death state (transitions immediately back to WAITING)

# Lifecycle timing (in game ticks, 1 tick = 600ms)
EGG_HATCH_TICKS = 100    # Ticks before egg hatches (~60 seconds)
DEATH_TICKS = 100        # Ticks after hatching before death (~60 seconds)

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
# EGG SPRITE SHEET (yoshieggs.raw: 128x160, 32x32 frames)
# =============================================================================
EGG_SPRITE_W = 32
EGG_SPRITE_H = 32
EGG_SHEET_W = 128
EGG_SHEET_H = 160

# Egg colors (rows)
EGG_GREEN = 0
EGG_RED = 1
EGG_BLUE = 2
EGG_YELLOW = 3
EGG_PINK = 4

# Egg sizes (column pairs)
EGG_SMALL = 0  # Columns 0-1
EGG_BIG = 1    # Columns 2-3

# Each egg animation has 2 frames
EGG_FRAME_COUNT = 2

# Helper to get egg frame coordinates
# Returns (x, y) of top-left corner for given color, size, and frame
def egg_frame_coords(color, size, frame):
    """Get sprite sheet coordinates for an egg frame.
    
    Args:
        color: EGG_GREEN, EGG_RED, EGG_BLUE, EGG_YELLOW, or EGG_PINK
        size: EGG_SMALL or EGG_BIG
        frame: 0 or 1 (animation frame)
    
    Returns:
        (x, y) tuple of top-left corner in sprite sheet
    """
    col = (size * 2) + frame  # 0,1 for small; 2,3 for big
    row = color
    return (col * EGG_SPRITE_W, row * EGG_SPRITE_H)

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
ASSET_EGGS = "yoshieggs.raw"
