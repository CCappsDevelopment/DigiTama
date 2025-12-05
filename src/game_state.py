# game_state.py
# Game state management: pet stats, tick system, menu state, lifecycle phases

import time
import random
import config


class PetStats:
    """Pet statistics that change over time."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all stats to initial values (called on hatch)."""
        # Core stats (0-100 scale, higher is better)
        # All start at 0 when hatched - player must care for pet
        self.hunger = 0
        self.happiness = 0
        self.discipline = 0
        self.energy = 0
        
        # Lifecycle
        self.age_ticks = 0     # Total game ticks lived (increases by 1 each tick)
        self.is_sleeping = False
        self.is_sick = False
        self.is_alive = True
        
        # Evolution tracking (for future)
        self.evolution_stage = 1  # 1=baby (just hatched)
        self.care_mistakes = 0    # Affects evolution path
    
    def tick(self):
        """Called every game tick (600ms) to update stats."""
        if not self.is_alive:
            return
        
        # Age always increases
        self.age_ticks += 1
        
        # Stat decay (adjust rates as needed)
        # Currently disabled until menu functions are implemented
        # if not self.is_sleeping:
        #     self.hunger = max(0, self.hunger - 0.1)
        #     self.happiness = max(0, self.happiness - 0.05)
        #     self.energy = max(0, self.energy - 0.02)
        # else:
        #     # Sleeping restores energy slowly
        #     self.energy = min(100, self.energy + 0.2)
        
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
    """Main game state container with lifecycle phase management."""
    
    def __init__(self):
        self.pet = PetStats()
        self.menu = MenuState()
        
        # Lifecycle phase (see config.PHASE_* constants)
        self.phase = config.PHASE_WAITING
        self.phase_ticks = 0  # Ticks spent in current phase
        
        # Egg state (set when transitioning to PHASE_EGG)
        self.egg_color = None  # config.EGG_GREEN, EGG_RED, etc.
        self.egg_size = None   # config.EGG_SMALL or EGG_BIG
        
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
            tick_occurred = True
            
            # Phase-specific tick logic
            self._tick_phase()
        
        return tick_occurred
    
    def _tick_phase(self):
        """Handle game tick based on current phase."""
        self.phase_ticks += 1
        
        if self.phase == config.PHASE_WAITING:
            # No tick logic in waiting state
            pass
        
        elif self.phase == config.PHASE_EGG:
            # Check if egg should hatch
            if self.phase_ticks >= config.EGG_HATCH_TICKS:
                self._transition_to_alive()
        
        elif self.phase == config.PHASE_ALIVE:
            # Update pet stats
            self.pet.tick()
            
            # Check for death (temporary: after DEATH_TICKS)
            if self.pet.age_ticks >= config.DEATH_TICKS:
                self._transition_to_dead()
        
        elif self.phase == config.PHASE_DEAD:
            # Immediately transition back to waiting
            self._transition_to_waiting()
    
    def start_game(self):
        """Start a new game by spawning a random egg.
        
        Called when BTN A + BTN C are pressed simultaneously.
        
        Returns:
            tuple: (egg_color, egg_size) for the spawned egg
        """
        # Choose random egg variant
        self.egg_color = random.randint(0, 4)  # 0-4: GREEN, RED, BLUE, YELLOW, PINK
        self.egg_size = random.randint(0, 1)   # 0-1: SMALL, BIG
        
        # Transition to egg phase
        self.phase = config.PHASE_EGG
        self.phase_ticks = 0
        
        return (self.egg_color, self.egg_size)
    
    def _transition_to_alive(self):
        """Transition from egg to alive state."""
        self.phase = config.PHASE_ALIVE
        self.phase_ticks = 0
        
        # Reset pet stats for new DigiTama
        self.pet.reset()
        
        # Clear egg state
        self.egg_color = None
        self.egg_size = None
    
    def _transition_to_dead(self):
        """Transition to dead state."""
        self.phase = config.PHASE_DEAD
        self.phase_ticks = 0
        self.pet.is_alive = False
    
    def _transition_to_waiting(self):
        """Transition back to waiting state (after death)."""
        self.phase = config.PHASE_WAITING
        self.phase_ticks = 0
        
        # Clear menu selection
        self.menu.clear_selection()
        
        # Reset pet for next game
        self.pet = PetStats()
    
    def is_menu_enabled(self):
        """Check if menu navigation should be enabled.
        
        Returns:
            bool: True if menu cycling is allowed
        """
        return self.phase == config.PHASE_ALIVE
    
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
