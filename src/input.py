# input.py
# Interrupt-driven input handling with debouncing and screen sleep management

import time
from machine import Pin, disable_irq, enable_irq
import config


class Input:
    """Interrupt-driven button input with debouncing and screen sleep.
    
    Uses hardware interrupts for instant button response. ISRs set flags
    that are consumed by the main loop via update().
    """
    
    # Button indices
    BTN_A = 0  # Next
    BTN_B = 1  # Confirm
    BTN_C = 2  # Back/Cancel
    
    def __init__(self, display, buttons):
        """Initialize interrupt-driven input handler.
        
        Args:
            display: Display object (for sleep on/off)
            buttons: Tuple of (btn_a, btn_b, btn_c) Pin objects
        """
        self.display = display
        self.btn_a, self.btn_b, self.btn_c = buttons
        
        # Flags set by ISR, read/cleared by main loop
        # Using list because ISR closures can't reassign outer variables
        self._pressed = [False, False, False]
        
        # Debounce: last press time per button (in ms)
        self._last_press = [0, 0, 0]
        
        # Screen sleep state
        self.screen_on = True
        self.last_activity = time.ticks_ms()
        
        # Attach interrupt handlers (falling edge = button pressed)
        self.btn_a.irq(trigger=Pin.IRQ_FALLING, handler=self._make_isr(0))
        self.btn_b.irq(trigger=Pin.IRQ_FALLING, handler=self._make_isr(1))
        self.btn_c.irq(trigger=Pin.IRQ_FALLING, handler=self._make_isr(2))
    
    def _make_isr(self, btn_idx):
        """Create an ISR closure for a specific button index.
        
        Returns a function suitable for pin.irq(handler=...).
        """
        # Capture the pin object for state checking
        pins = [self.btn_a, self.btn_b, self.btn_c]
        pin_obj = pins[btn_idx]
        
        def isr(pin):
            # ISR must be fast - only set flag with debounce check
            # Also verify pin is actually LOW (pressed) to filter release bounce
            if pin_obj.value() == 0:  # Still pressed (active-low)
                now = time.ticks_ms()
                if time.ticks_diff(now, self._last_press[btn_idx]) > config.DEBOUNCE_MS:
                    self._pressed[btn_idx] = True
                    self._last_press[btn_idx] = now
        return isr
    
    def update(self):
        """Consume pending button presses and manage screen sleep.
        
        Call once per game loop iteration.
        
        Returns:
            tuple: (screen_on, just_woke, pressed)
                - screen_on: bool, is screen currently on
                - just_woke: bool, did screen just wake up
                - pressed: tuple of (btn_a, btn_b, btn_c) pressed states
        """
        # Atomically read and clear flags to prevent race conditions
        # Disable interrupts during read-modify-write
        irq_state = disable_irq()
        pressed = (self._pressed[0], self._pressed[1], self._pressed[2])
        self._pressed[0] = False
        self._pressed[1] = False
        self._pressed[2] = False
        enable_irq(irq_state)
        
        any_pressed = any(pressed)
        just_woke = False
        now = time.ticks_ms()
        
        if any_pressed:
            self.last_activity = now
            
            if not self.screen_on:
                # Wake up the screen
                self.display.display_on()
                self.screen_on = True
                just_woke = True
                # Clear presses so wake doesn't trigger action
                pressed = (False, False, False)
        
        # Check for timeout
        if self.screen_on:
            if time.ticks_diff(now, self.last_activity) >= config.SCREEN_TIMEOUT_MS:
                self.display.display_off()
                self.screen_on = False
        
        return self.screen_on, just_woke, pressed
    
    def reset_timeout(self):
        """Reset the screen timeout timer."""
        self.last_activity = time.ticks_ms()
    
    def cleanup(self):
        """Disable interrupts. Call on shutdown."""
        self.btn_a.irq(handler=None)
        self.btn_b.irq(handler=None)
        self.btn_c.irq(handler=None)
