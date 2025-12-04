# game_state.py
# Game state management: pet stats, tick system, menu state

import time
import config


class PetStats:
    """Pet statistics that change over time."""
    
    def __init__(self):
        # Core stats (0-100 scale, higher is better)
        self.hunger = 100      # Decreases over time, feed to restore
        self.happiness = 100   # Decreases over time, play to restore
        self.discipline = 50   # Can go up or down based on training
        self.energy = 100      # Decreases with activity, sleep to restore
        
        # Lifecycle
        self.age_ticks = 0     # Total game ticks lived
        self.is_sleeping = False
        self.is_sick = False
        self.is_alive = True
        
        # Evolution tracking (for future)
        self.evolution_stage = 0  # 0=egg, 1=baby, 2=child, 3=teen, 4=adult
        self.care_mistakes = 0    # Affects evolution path
    
    def tick(self):
        """Called every game tick (600ms) to update stats."""
        if not self.is_alive:
            return
        
        self.age_ticks += 1
        
        # Stat decay (adjust rates as needed)
        if not self.is_sleeping:
            self.hunger = max(0, self.hunger - 0.1)
            self.happiness = max(0, self.happiness - 0.05)
            self.energy = max(0, self.energy - 0.02)
        else:
            # Sleeping restores energy slowly
            self.energy = min(100, self.energy + 0.2)
        
        # Check for critical conditions
        if self.hunger <= 0 or self.happiness <= 0:
            self.care_mistakes += 1
        
        # Sickness chance when stats are low
        if self.hunger < 20 or self.happiness < 20:
            # Could add random sickness chance here
            pass
    
    def feed(self):
        """Feed the pet."""
        if self.is_sleeping or not self.is_alive:
            return False
        self.hunger = min(100, self.hunger + 20)
        return True
    
    def play(self):
        """Play with the pet."""
        if self.is_sleeping or not self.is_alive:
            return False
        self.happiness = min(100, self.happiness + 15)
        self.energy = max(0, self.energy - 5)
        return True
    
    def train(self):
        """Train/discipline the pet."""
        if self.is_sleeping or not self.is_alive:
            return False
        self.discipline = min(100, self.discipline + 5)
        self.happiness = max(0, self.happiness - 5)
        return True
    
    def toggle_sleep(self):
        """Toggle sleep state."""
        if not self.is_alive:
            return False
        self.is_sleeping = not self.is_sleeping
        return True
    
    def heal(self):
        """Heal sickness."""
        if not self.is_alive:
            return False
        self.is_sick = False
        return True


class MenuState:
    """Menu navigation state."""
    
    def __init__(self):
        self.selected = None  # None or 0-9
        self.in_submenu = False
        self.submenu_type = None
    
    def select_next(self):
        """Move to next menu item."""
        if self.selected is None:
            self.selected = 0
        else:
            self.selected = (self.selected + 1) % len(config.MENU_RECTS)
    
    def select_prev(self):
        """Move to previous menu item."""
        if self.selected is None:
            self.selected = len(config.MENU_RECTS) - 1
        else:
            self.selected = (self.selected - 1) % len(config.MENU_RECTS)
    
    def clear_selection(self):
        """Clear current selection."""
        self.selected = None
        self.in_submenu = False
        self.submenu_type = None
    
    def confirm(self):
        """Confirm current selection.
        
        Returns:
            int or None: The confirmed menu item index, or None
        """
        if self.selected is not None:
            return self.selected
        return None


class GameState:
    """Main game state container."""
    
    def __init__(self):
        self.pet = PetStats()
        self.menu = MenuState()
        
        # Tick timing
        self.last_tick_time = time.ticks_ms()
        self.tick_count = 0
        
        # Sprite animation timing (separate from game tick)
        self.last_sprite_time = time.ticks_ms()
    
    def update(self):
        """Update game state. Call every frame.
        
        Returns:
            bool: True if a game tick occurred this frame
        """
        now = time.ticks_ms()
        tick_occurred = False
        
        # Check for game tick (600ms)
        if time.ticks_diff(now, self.last_tick_time) >= config.GAME_TICK_MS:
            self.last_tick_time = now
            self.tick_count += 1
            self.pet.tick()
            tick_occurred = True
        
        return tick_occurred
    
    def should_advance_sprite(self):
        """Check if sprite animation should advance.
        
        Returns:
            bool: True if sprite frame should advance
        """
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_sprite_time) >= config.SPRITE_FRAME_DELAY_MS:
            self.last_sprite_time = now
            return True
        return False
    
    def handle_menu_action(self, menu_index):
        """Handle a confirmed menu action.
        
        Args:
            menu_index: The menu item that was activated (0-9)
        """
        # TODO: Map menu indices to actions
        # For now, just print
        # print(f"Menu action: {menu_index}")
        
        # Example mapping (to be refined):
        # 0: Feed    5: Stats
        # 1: Play    6: Discipline
        # 2: Clean   7: Medical
        # 3: Sleep   8: Settings
        # 4: ???     9: ???
        
        if menu_index == 0:
            self.pet.feed()
        elif menu_index == 1:
            self.pet.play()
        elif menu_index == 3:
            self.pet.toggle_sleep()
        elif menu_index == 6:
            self.pet.train()
        elif menu_index == 7:
            self.pet.heal()
