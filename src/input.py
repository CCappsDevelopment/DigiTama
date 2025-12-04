# input.py
# Input handling: button edge detection, debouncing, screen sleep management

import time
import config


class Input:
    """Handles all input processing with debouncing and screen sleep."""
    
    # Button indices
    BTN_A = 0  # Next
    BTN_B = 1  # Confirm
    BTN_C = 2  # Back/Cancel
    
    def __init__(self, display, buttons):
        """Initialize input handler.
        
        Args:
            display: Display object (for sleep on/off)
            buttons: Tuple of (btn_a, btn_b, btn_c) Pin objects
        """
        self.display = display
        self.btn_a, self.btn_b, self.btn_c = buttons
        
        # Previous button states for edge detection
        self.prev_state = (1, 1, 1)  # All released (pull-up)
        
        # Debounce: last press time per button
        self.last_press_time = [0, 0, 0]
        
        # Pending presses (accumulated between update() calls)
        self.pending_presses = [False, False, False]
        
        # Screen sleep state
        self.screen_on = True
        self.last_activity = time.ticks_ms()
    
    def poll(self):
        """Poll buttons and accumulate presses. Call this frequently (~5ms)."""
        current_time = time.ticks_ms()
        current_state = (
            self.btn_a.value(),
            self.btn_b.value(),
            self.btn_c.value()
        )
        
        for i in range(3):
            # Edge detection: was released (1), now pressed (0)
            if self.prev_state[i] == 1 and current_state[i] == 0:
                # Debounce check
                if time.ticks_diff(current_time, self.last_press_time[i]) > config.DEBOUNCE_MS:
                    self.pending_presses[i] = True
                    self.last_press_time[i] = current_time
        
        self.prev_state = current_state
    
    def update(self):
        """Process accumulated presses and manage screen sleep.
        
        Call once per game loop iteration (after polling).
        
        Returns:
            tuple: (screen_on, just_woke, pressed)
                - screen_on: bool, is screen currently on
                - just_woke: bool, did screen just wake up
                - pressed: tuple of (btn_a, btn_b, btn_c) pressed states
        """
        # One final poll to catch recent presses
        self.poll()
        
        # Collect pending presses and reset
        pressed = tuple(self.pending_presses)
        self.pending_presses = [False, False, False]
        
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
