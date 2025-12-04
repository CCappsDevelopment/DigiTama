# screen_sleep.py
import time


class ScreenSleepManager:
    """Manages OLED screen timeout to prevent burn-in and save power.
    
    Usage:
        sleep_mgr = ScreenSleepManager(display, [btn_a, btn_b, btn_c], timeout_ms=60_000)
        
        # In main loop:
        screen_on, just_woke = sleep_mgr.update()
        if not screen_on:
            continue  # Skip rendering when screen is off
        if just_woke:
            pass  # Optional: handle wake event (e.g., skip button action)
    """
    
    def __init__(self, display, buttons, timeout_ms=60_000):
        self.display = display
        self.buttons = [b for b in buttons if b is not None]
        self.timeout_ms = timeout_ms

        now = time.ticks_ms()
        self.last_activity = now
        self.screen_on = True

        # Last values for edge detection
        self.last_values = {id(b): b.value() for b in self.buttons}

    def update(self):
        """Check for button activity and manage screen state.
        
        Returns:
            tuple: (screen_on: bool, just_woke: bool)
                - screen_on: True if screen is currently on
                - just_woke: True if screen just turned on this frame
        """
        now = time.ticks_ms()
        any_press = False

        for b in self.buttons:
            key = id(b)
            current = b.value()
            last = self.last_values.get(key, 1)
            # Detect press (1→0 edge)
            if last == 1 and current == 0:
                any_press = True
            self.last_values[key] = current

        just_woke = False

        if any_press:
            self.last_activity = now
            if not self.screen_on:
                self.display.display_on()
                self.screen_on = True
                just_woke = True

        if self.screen_on and time.ticks_diff(now, self.last_activity) >= self.timeout_ms:
            self.display.display_off()
            self.screen_on = False

        return self.screen_on, just_woke

    def reset_timer(self):
        """Reset the inactivity timer (call when handling button events)."""
        self.last_activity = time.ticks_ms()
