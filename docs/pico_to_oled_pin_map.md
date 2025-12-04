## OLED Connections

| Pico Pin       | OLED Pin  | Map                    |
|----------------|-----------|-------------------------|
| P36 - 3V3 (Out) | Vin       | Power                  |
| P38 - GND       | GND       | Ground (OLED)          |
| P04 - GP2       | SPI SCK   | Clock                  |
| P05 - GP3       | SPI MOSI  | Master-in, Slave-Out   |
| P07 - GP5       | TCS       | Chip select            |
| P09 - GP6       | DC        | Data/Command           |
| P10 - GP7       | RST       | Reset                  |

## Component Connections

| Pico Pin       | Component | Map                      |
|----------------|------------|---------------------------|
| P38 - GND       | GND Rail  | Breadboard ground rail    |
| P14 - GP10      | BTN A     | Button A (Next)           |
| P15 - GP11      | BTN B     | Button B (Confirm)        |
| P16 - GP12      | NO-OP     | Planned BTN C (N/A)       |


## Vocabulary

* SCK (serial clock, Pico GP2 → OLED SCK)

	- SPI is synchronous: the master (your Pico) provides a clock signal so both sides know exactly when to sample each bit.
	- SCK is that clock; every edge (usually rising or falling, depending on mode) tells the SSD1351 “read the next bit on MOSI now”.
	- Without SCK, the OLED would see changing data levels but have no idea where one bit ends and the next begins, so no bytes/commands could be reconstructed.

* MOSI (Master‑Out Slave‑In, Pico GP3 → OLED MOSI/DI/SI/TX)

	- This is the data line going from the Pico to the OLED.
	- When you send a command or pixel data, the Pico puts bits on MOSI, and the SSD1351 samples those bits in sync with SCK to assemble bytes (like “draw pixel”, “set window”, or raw color values).
	- The name changes (MOSI, SI, DI, TX) but all mean “input data line for the display, driven by the controller”.
 
* CS / TCS (chip‑select, Pico GP5 → OLED CS)

	- The SPI bus can have multiple devices on the same SCK and MOSI lines; CS is how you select which one is currently active.
	- When CS is low, the OLED listens to SCK/MOSI and treats incoming bits as commands/data; when CS is high, it ignores the bus.
	- In your simple setup there’s only one SPI device, but CS is still used to clearly bracket transactions (e.g., “from this moment until CS goes high again, these bytes belong to the display”).

* DC (data/command, Pico GP6 → OLED DC)

	- The SSD1351 uses the same SPI wires for both commands (like “set column address”) and data (pixel color values), so it needs a way to distinguish them.
		> DC = 0 (low) means “the next byte(s) are command bytes”.
    		> DC = 1 (high) means “the next byte(s) are data bytes”.
	- A typical operation looks like:
		> Set DC low, send one command byte (e.g., “write RAM”).
        	> Set DC high, stream lots of data bytes (the actual pixel colors to fill the screen).

* RST (reset, Pico GP7 → OLED RST)

	- RST is a hardware reset input to the SSD1351 controller.
	- Pulling RST low briefly, then back high, forces the controller into a known power‑on state, clearing any weird states from power‑up glitches or bad commands.
	- Many driver libraries begin by toggling RST (low for, say, 10–50 ms, then high) before sending the initialization command sequence, to guarantee the display starts from a clean slate.

