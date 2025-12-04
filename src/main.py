# main.py
#
# DigiTama Virtual Pet - Entry Point
# Raspberry Pi Pico 2 + SSD1351 128x128 OLED
#
# This is the entry point that runs when the Pico boots.
# It imports and starts the main game.

from game import main

if __name__ == "__main__":
    main()
