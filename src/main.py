# main.py
#
# Boilerplate for Pico 2 + SSD1351 + buttons.
# Put experiments in separate modules and call them from run_demo().

from machine import Pin, SPI
import time
import ssd1351


# ---------- Pin map (your wiring) ----------

# OLED / SPI
SPI_ID   = 0
PIN_SCK  = 2    # GP2  -> SCK
PIN_MOSI = 3    # GP3  -> MOSI
PIN_MISO = 4    # GP4  -> (unused by OLED)
PIN_CS   = 5    # GP5  -> TCS
PIN_DC   = 6    # GP6  -> DC
PIN_RST  = 7    # GP7  -> RST

# Buttons (one leg to GPIO, opposite leg to GND rail)
PIN_BTN_A = 10  # GP10 -> BTN A (Next)
PIN_BTN_B = 11  # GP11 -> BTN B (Confirm)
PIN_BTN_C = 12 # GP12 -> BTN C (Back/Cancel)


# ---------- Color helper ----------

def color565(r, g, b):
    # Same format the driver uses
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | (b >> 3)

BLACK = color565(0, 0, 0)
RED   = color565(255, 0, 0)
GREEN = color565(0, 255, 0)
BLUE  = color565(0, 0, 255)


# ---------- Hardware init ----------

def init_spi():
    spi = SPI(
        SPI_ID,
        baudrate=16_000_000,
        polarity=0,
        phase=0,
        sck=Pin(PIN_SCK),
        mosi=Pin(PIN_MOSI),
        miso=Pin(PIN_MISO),
    )
    return spi


def init_display(spi):
    cs  = Pin(PIN_CS, Pin.OUT)
    dc  = Pin(PIN_DC, Pin.OUT)
    rst = Pin(PIN_RST, Pin.OUT)

    # Driver: Display(spi, cs, dc, rst, width=128, height=128)
    display = ssd1351.Display(spi, cs, dc, rst, width=128, height=128)
    display.clear(BLACK)
    return display


def init_buttons():
    # Internal pull-ups; pressed = 0, released = 1
    btn_a = Pin(PIN_BTN_A, Pin.IN, Pin.PULL_UP)
    btn_b = Pin(PIN_BTN_B, Pin.IN, Pin.PULL_UP)
    btn_c = Pin(PIN_BTN_C, Pin.IN, Pin.PULL_UP)
    return btn_a, btn_b, btn_c


# ---------- Demo selector ----------

def run_demo(display, btn_a, btn_b, btn_c):
    """
    Default demo: change screen color based on buttons.
    Later you can replace this with:
        import demo_sprites
        demo_sprites.run(display, btn_a, btn_b, btn_c)
    """
    import demo_sprite
    demo_sprite.run(display, btn_a, btn_b, btn_c)

    #import demo_menu
    #demo_menu.run(display, btn_a, btn_b, btn_c)

    #import demo_bgimage
    #demo_bgimage.run(display, btn_a, btn_b)

    #import demo_water
    #demo_water.run(display, btn_a, btn_b)

    print("Button color demo ready (A/B)")

    display.clear(BLACK)
    last_color = BLACK
    last_a = btn_a.value()
    last_b = btn_b.value()
    last_c = btn_c.value()

    while True:
        va = btn_a.value()
        vb = btn_b.value()
        vc = btn_c.value()

        # Edge-detect presses (1 -> 0)
        if last_a == 1 and va == 0:
            print("BTN A pressed -> RED")
            display.clear(RED)
            last_color = RED

        if last_b == 1 and vb == 0:
            print("BTN B pressed -> GREEN")
            display.clear(GREEN)
            last_color = GREEN
        
        if last_c == 1 and vc == 0:
            print("BTN C pressed -> BLUE")
            display.clear(BLUE)
            last_color = BLUE

        last_a = va
        last_b = vb
        last_c = vc

        time.sleep(0.02)  # ~50 Hz polling


# ---------- Main entry ----------

def main():
    print("Main starting")

    spi = init_spi()
    display = init_display(spi)
    btn_a, btn_b, btn_c = init_buttons()

    run_demo(display, btn_a, btn_b, btn_c)


if __name__ == "__main__":
    main()
