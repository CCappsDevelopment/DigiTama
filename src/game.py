# game.py
# Main game loop: ties together all modules

import time
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
    
    def init(self):
        """Initialize all game systems."""
        print("DigiTama starting...")
        
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
        
        print("DigiTama ready!")
    
    def run(self):
        """Main game loop."""
        self.running = True
        last_render_time = time.ticks_ms()
        
        while self.running:
            # Poll buttons frequently for responsive input
            self.input.poll()
            
            # Check if it's time to update/render (maintain ~12.5 FPS for animations)
            now = time.ticks_ms()
            elapsed = time.ticks_diff(now, last_render_time)
            
            if elapsed >= config.BG_FRAME_DELAY_MS:
                last_render_time = now
                self._update()
                self._render()
            else:
                # Short sleep to prevent CPU spinning, but still poll fast
                time.sleep_ms(config.INPUT_POLL_MS)
    
    def _update(self):
        """Update game logic."""
        # Process input and screen sleep
        screen_on, just_woke, pressed = self.input.update()
        
        # Update game tick (600ms timer for stats) - even when screen is off
        tick_occurred = self.state.update()
        # if tick_occurred:
            # Debug: print stats every tick (remove later)
            # print(f"Tick {self.state.tick_count}: H={self.state.pet.hunger:.1f}")
        
        if not screen_on:
            # Screen is off - skip input handling and animation
            return
        
        if just_woke:
            # Just woke up - don't process button actions this frame
            return
        
        # Unpack button states
        btn_a, btn_b, btn_c = pressed
        
        # Handle button presses
        if btn_a:  # Next
            self.state.menu.select_next()
            # print(f"Selected: {self.state.menu.selected}")
        
        if btn_b:  # Confirm
            action = self.state.menu.confirm()
            if action is not None:
                self.state.handle_menu_action(action)
        
        if btn_c:  # Back/Cancel
            self.state.menu.clear_selection()
            print("Selection cleared")
        
        # Update sprite animation timing
        if self.state.should_advance_sprite():
            self.graphics.advance_sprite_frame()
    
    def _render(self):
        """Render current frame."""
        # Don't render if screen is off
        if not self.input.screen_on:
            return
        
        # Render frame with current menu selection
        self.graphics.render_frame(
            selected_menu=self.state.menu.selected
        )
    
    def stop(self):
        """Stop the game loop."""
        self.running = False
    
    def cleanup(self):
        """Clean up resources."""
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
