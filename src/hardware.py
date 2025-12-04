# hardware.py
# Hardware abstraction layer for Raspberry Pi Pico 2 + SSD1351 OLED

from machine import Pin, SPI
import ssd1351
import config


class Hardware:
    """Encapsulates all hardware initialization and access."""
    
    def __init__(self):
        self.spi = None
        self.display = None
        self.btn_a = None
        self.btn_b = None
        self.btn_c = None
    
    def init(self):
        """Initialize all hardware components."""
        self._init_spi()
        self._init_display()
        self._init_buttons()
        print("Hardware initialized")
    
    def _init_spi(self):
        """Initialize SPI bus."""
        self.spi = SPI(
            config.SPI_ID,
            baudrate=config.SPI_BAUDRATE,
            polarity=config.SPI_POLARITY,
            phase=config.SPI_PHASE,
            sck=Pin(config.PIN_SCK),
            mosi=Pin(config.PIN_MOSI),
            miso=Pin(config.PIN_MISO),
        )
    
    def _init_display(self):
        """Initialize OLED display."""
        cs = Pin(config.PIN_CS, Pin.OUT)
        dc = Pin(config.PIN_DC, Pin.OUT)
        rst = Pin(config.PIN_RST, Pin.OUT)
        
        self.display = ssd1351.Display(
            self.spi, cs, dc, rst,
            width=config.WIDTH,
            height=config.HEIGHT
        )
        self.display.clear(config.BLACK)
    
    def _init_buttons(self):
        """Initialize buttons with internal pull-ups."""
        self.btn_a = Pin(config.PIN_BTN_A, Pin.IN, Pin.PULL_UP)
        self.btn_b = Pin(config.PIN_BTN_B, Pin.IN, Pin.PULL_UP)
        self.btn_c = Pin(config.PIN_BTN_C, Pin.IN, Pin.PULL_UP)
    
    def get_buttons(self):
        """Return tuple of button pins."""
        return (self.btn_a, self.btn_b, self.btn_c)
    
    def cleanup(self):
        """Clean up hardware resources."""
        if self.display:
            self.display.cleanup()
