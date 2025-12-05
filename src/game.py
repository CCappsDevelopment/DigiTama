# game.py
# Main game loop: ties together all modules

import time
import random
import config
from hardware import Hardware
from graphics import Graphics
from input import Input
from game_state import GameState


class Game:
    """Main game controller."""
    
    def __init__(self):
        self.hardware = Hardware()
        self.graphics = None
        self.input = None
        self.state = None
        self.running = False
        
        # Track phase transitions for rendering
        self._last_phase = None
    
    def init(self):
        """Initialize all game systems."""
        print("DigiTama starting...")
        
        # Seed random number generator for egg selection variety
        random.seed(time.ticks_ms())
        
        # Initialize hardware
        self.hardware.init()
        
        # Initialize subsystems
        self.graphics = Graphics(self.hardware.display)
        self.graphics.load_assets()
        
        self.input = Input(
            self.hardware.display,
            self.hardware.get_buttons()
        )
        
        self.state = GameState()
        self._last_phase = self.state.phase
        
        # Do initial full-screen render (no sprite in PHASE_WAITING)
        self.graphics.render_initial(show_sprite=False)
        
        print("DigiTama ready! Press BTN A + BTN C to start.")
    
    def run(self):
        """Main game loop."""
        self.running = True
        last_update_time = time.ticks_ms()
        
        while self.running:
            # Check if it's time to update/render
            now = time.ticks_ms()
            elapsed = time.ticks_diff(now, last_update_time)
            
            if elapsed >= config.BG_FRAME_DELAY_MS:
                last_update_time = now
                self._update()
                self._render()
            else:
                # Sleep between updates - interrupts will still fire and set flags
                time.sleep_ms(config.INPUT_POLL_MS)
    
    def _update(self):
        """Update game logic."""
        # Process input and screen sleep
        screen_on, just_woke, pressed = self.input.update()
        
        # Store previous phase to detect transitions
        prev_phase = self.state.phase
        
        # Update game tick (600ms timer for stats/lifecycle) - even when screen is off
        tick_occurred = self.state.update()
        
        # Check for phase transitions
        if self.state.phase != prev_phase:
            self._handle_phase_transition(prev_phase, self.state.phase)
        
        if not screen_on:
            # Screen is off - skip input handling and animation
            return
        
        if just_woke:
            # Just woke up - don't process button actions this frame
            return
        
        # Unpack button states
        btn_a, btn_b, btn_c = pressed
        
        # Phase-specific input handling
        self._handle_input(btn_a, btn_b, btn_c)
        
        # Update sprite/egg animation timing
        if self.state.should_advance_sprite():
            if self.state.phase == config.PHASE_EGG:
                self.graphics.advance_egg_frame()
            elif self.state.phase == config.PHASE_ALIVE:
                self.graphics.advance_sprite_frame()
    
    def _handle_input(self, btn_a, btn_b, btn_c):
        """Handle button input based on current game phase."""
        phase = self.state.phase
        
        if phase == config.PHASE_WAITING:
            # Check for simultaneous BTN A + BTN C to start game
            if btn_a and btn_c:
                egg_color, egg_size = self.state.start_game()
                self.graphics.set_egg(egg_color, egg_size)
                print(f"Egg spawned! Color={egg_color}, Size={egg_size}")
        
        elif phase == config.PHASE_EGG:
            # No input actions during egg phase
            # (egg hatches automatically after timer)
            pass
        
        elif phase == config.PHASE_ALIVE:
            # Normal gameplay - menu navigation enabled
            if btn_a:  # Next
                old_selection = self.state.menu.selected
                self.state.menu.select_next()
                self.graphics.update_menu_selection(old_selection, self.state.menu.selected)
            
            if btn_b:  # Confirm
                action = self.state.menu.confirm()
                if action is not None:
                    self.state.handle_menu_action(action)
            
            if btn_c:  # Back/Cancel
                old_selection = self.state.menu.selected
                self.state.menu.clear_selection()
                self.graphics.update_menu_selection(old_selection, None)
        
        elif phase == config.PHASE_DEAD:
            # No input during death (immediate transition)
            pass
    
    def _handle_phase_transition(self, old_phase, new_phase):
        """Handle visual updates when game phase changes."""
        print(f"Phase transition: {old_phase} -> {new_phase}")
        
        if new_phase == config.PHASE_WAITING:
            # Clear sprite region (pet died, return to waiting)
            self.graphics.clear_sprite_region()
            print("Awaiting new game... Press BTN A + BTN C to start.")
        
        elif new_phase == config.PHASE_EGG:
            # Egg sprite setup is handled in _handle_input when start_game() is called
            pass
        
        elif new_phase == config.PHASE_ALIVE:
            # Egg hatched! Switch to pet sprite
            # Clear egg and draw initial pet sprite
            self.graphics.sprite_frame_idx = 0
            self.graphics.current_sprite_frame = -1  # Force redraw
            print("Egg hatched! DigiTama born!")
        
        elif new_phase == config.PHASE_DEAD:
            # Pet died - this will immediately transition to WAITING
            print("DigiTama died!")
    
    def _render(self):
        """Render only changed regions (dirty rectangles)."""
        # Don't render if screen is off
        if not self.input.screen_on:
            return
        
        phase = self.state.phase
        
        if phase == config.PHASE_WAITING:
            # No sprite to render
            pass
        
        elif phase == config.PHASE_EGG:
            # Update egg animation
            self.graphics.update_egg()
        
        elif phase == config.PHASE_ALIVE:
            # Update pet sprite animation
            self.graphics.update_sprite()
        
        elif phase == config.PHASE_DEAD:
            # No rendering during death transition
            pass
    
    def stop(self):
        """Stop the game loop."""
        self.running = False
    
    def cleanup(self):
        """Clean up resources."""
        if self.input:
            self.input.cleanup()  # Disable button IRQs
        if self.hardware:
            self.hardware.cleanup()


def main():
    """Entry point."""
    game = Game()
    try:
        game.init()
        game.run()
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        game.cleanup()


if __name__ == "__main__":
    main()
