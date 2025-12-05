# graphics.py
# Graphics rendering with dirty rectangle optimization
# Only updates changed regions (sprite area, menu highlights) instead of full screen

import config


class Graphics:
    """Handles all rendering operations with dirty rectangle optimization."""
    
    def __init__(self, display):
        self.display = display
        
        # Cached assets
        self.base_frame = None      # Pre-composited background + menu (clean copy)
        self.sprite_buf = None      # Main sprite sheet (yoshisprite.raw)
        self.egg_buf = None         # Egg sprite sheet (yoshieggs.raw)
        
        # Current display state (what's actually on screen)
        self.current_menu_selection = None
        self.current_sprite_frame = 0
        self.current_sprite_row = 0
        
        # Target state (what we want to display)
        self.sprite_frame_idx = 0
        self.sprite_row = config.CURRENT_ANIM  # Use configured animation row
        
        # Egg animation state
        self.egg_frame_idx = 0
        self.egg_color = None
        self.egg_size = None
        self.current_egg_frame = -1  # -1 means no egg currently displayed
        
        # Track what type of sprite is currently displayed
        # None = nothing, 'egg' = egg sprite, 'pet' = main sprite
        self.displayed_sprite_type = None
        
        # Track if initial full render has been done
        self.initialized = False
    
    def load_assets(self):
        """Load and pre-composite all static assets."""
        print("Loading assets...")
        
        # Load background
        bg_buf = self._load_raw(
            config.ASSET_BG,
            config.BUF_SIZE
        )
        
        # Load menu overlay (if configured)
        if config.ASSET_MENU:
            menu_buf = self._load_raw(
                config.ASSET_MENU,
                config.BUF_SIZE
            )
            # Pre-composite: apply menu onto background with colorkey
            print("Compositing base frame...")
            self._overlay_colorkey(bg_buf, menu_buf)
        
        self.base_frame = bg_buf
        
        # Load main sprite sheet
        sprite_size = config.SPRITE_SHEET_W * config.SPRITE_SHEET_H * config.BPP
        self.sprite_buf = self._load_raw(
            config.ASSET_SPRITE,
            sprite_size
        )
        
        # Load egg sprite sheet
        egg_size = config.EGG_SHEET_W * config.EGG_SHEET_H * config.BPP
        self.egg_buf = self._load_raw(
            config.ASSET_EGGS,
            egg_size
        )
        
        print("Assets loaded")
    
    def _load_raw(self, path, expected_size):
        """Load a raw RGB565 file."""
        with open(path, "rb") as f:
            data = f.read()
        if len(data) != expected_size:
            raise ValueError(f"Unexpected size for {path}: {len(data)}")
        return bytearray(data)
    
    def render_initial(self, show_sprite=True):
        """Render the full frame once at startup.
        
        Args:
            show_sprite: If True, draw initial pet sprite. If False, only show background.
        """
        # Push full base frame to display
        self.display.block(0, 0, config.WIDTH - 1, config.HEIGHT - 1, self.base_frame)
        
        if show_sprite:
            # Draw initial sprite
            self._update_sprite_region(self.sprite_row, self.sprite_frame_idx)
            self.current_sprite_row = self.sprite_row
            self.current_sprite_frame = self.sprite_frame_idx
            self.displayed_sprite_type = 'pet'
        else:
            # No sprite displayed initially
            self.displayed_sprite_type = None
        
        self.initialized = True
    
    def update_menu_selection(self, old_selection, new_selection):
        """Update only the menu rectangles that changed."""
        # Restore old selection (un-invert)
        if old_selection is not None:
            self._restore_and_push_rect(config.MENU_RECTS[old_selection])
        
        # Apply new selection (invert)
        if new_selection is not None:
            self._invert_and_push_rect(config.MENU_RECTS[new_selection])
        
        self.current_menu_selection = new_selection
    
    def update_sprite(self):
        """Update the sprite region if animation frame changed."""
        if (self.sprite_frame_idx != self.current_sprite_frame or
            self.sprite_row != self.current_sprite_row):
            
            # Redraw sprite region with new frame
            self._update_sprite_region(self.sprite_row, self.sprite_frame_idx)
            
            self.current_sprite_frame = self.sprite_frame_idx
            self.current_sprite_row = self.sprite_row
    
    def _update_sprite_region(self, anim_row, frame_index):
        """Redraw the sprite region (scaled to display size)."""
        x0 = config.SPRITE_X
        y0 = config.SPRITE_Y
        x1 = x0 + config.SPRITE_DISPLAY_W - 1
        y1 = y0 + config.SPRITE_DISPLAY_H - 1
        
        # Create buffer for the scaled sprite region
        region_w = config.SPRITE_DISPLAY_W
        region_h = config.SPRITE_DISPLAY_H
        region_size = region_w * region_h * config.BPP
        region_buf = bytearray(region_size)
        
        # Copy base frame pixels for this region
        for dy in range(region_h):
            src_y = y0 + dy
            src_row_start = (src_y * config.WIDTH + x0) * config.BPP
            dst_row_start = dy * region_w * config.BPP
            
            for dx in range(region_w):
                si = src_row_start + dx * config.BPP
                di = dst_row_start + dx * config.BPP
                region_buf[di] = self.base_frame[si]
                region_buf[di + 1] = self.base_frame[si + 1]
        
        # Blit scaled sprite onto region buffer
        self._blit_sprite_to_region_scaled(region_buf, region_w, anim_row, frame_index)
        
        # Push just this region to display
        self.display.block(x0, y0, x1, y1, region_buf)
    
    def _blit_sprite_to_region_scaled(self, region_buf, region_w, anim_row, frame_index):
        """Blit sprite frame onto region buffer with scaling.
        
        Each source pixel is rendered as a SPRITE_SCALE x SPRITE_SCALE block.
        """
        sx0 = config.SPRITE_W * frame_index
        sy0 = config.SPRITE_H * anim_row
        scale = config.SPRITE_SCALE
        
        for sy in range(config.SPRITE_H):
            sheet_row_start = ((sy0 + sy) * config.SPRITE_SHEET_W + sx0) * config.BPP
            
            for sx in range(config.SPRITE_W):
                si = sheet_row_start + sx * config.BPP
                hi = self.sprite_buf[si]
                lo = self.sprite_buf[si + 1]
                color = (hi << 8) | lo
                if color == config.TRANSPARENT_KEY:
                    continue
                
                # Write scale x scale block of pixels
                dst_x = sx * scale
                dst_y = sy * scale
                for by in range(scale):
                    row_start = (dst_y + by) * region_w * config.BPP
                    for bx in range(scale):
                        di = row_start + (dst_x + bx) * config.BPP
                        region_buf[di] = hi
                        region_buf[di + 1] = lo
    
    def _restore_and_push_rect(self, rect):
        """Restore a rectangle from base_frame and push to display."""
        x0, y0, x1, y1 = rect
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(config.WIDTH - 1, x1)
        y1 = min(config.HEIGHT - 1, y1)
        
        w = x1 - x0 + 1
        h = y1 - y0 + 1
        region_buf = bytearray(w * h * config.BPP)
        
        # Copy from base_frame
        for dy in range(h):
            src_y = y0 + dy
            src_row_start = (src_y * config.WIDTH + x0) * config.BPP
            dst_row_start = dy * w * config.BPP
            
            for dx in range(w):
                si = src_row_start + dx * config.BPP
                di = dst_row_start + dx * config.BPP
                region_buf[di] = self.base_frame[si]
                region_buf[di + 1] = self.base_frame[si + 1]
        
        self.display.block(x0, y0, x1, y1, region_buf)
    
    def _invert_and_push_rect(self, rect):
        """Invert a rectangle and push to display."""
        x0, y0, x1, y1 = rect
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(config.WIDTH - 1, x1)
        y1 = min(config.HEIGHT - 1, y1)
        
        w = x1 - x0 + 1
        h = y1 - y0 + 1
        region_buf = bytearray(w * h * config.BPP)
        
        # Copy from base_frame and invert
        for dy in range(h):
            src_y = y0 + dy
            src_row_start = (src_y * config.WIDTH + x0) * config.BPP
            dst_row_start = dy * w * config.BPP
            
            for dx in range(w):
                si = src_row_start + dx * config.BPP
                di = dst_row_start + dx * config.BPP
                hi = self.base_frame[si]
                lo = self.base_frame[si + 1]
                c = (hi << 8) | lo
                c ^= 0xFFFF
                region_buf[di] = (c >> 8) & 0xFF
                region_buf[di + 1] = c & 0xFF
        
        self.display.block(x0, y0, x1, y1, region_buf)
    
    def advance_sprite_frame(self):
        """Advance to next sprite animation frame."""
        frame_count = config.ANIM_FRAME_COUNTS.get(self.sprite_row, 8)
        self.sprite_frame_idx = (self.sprite_frame_idx + 1) % frame_count
    
    def advance_egg_frame(self):
        """Advance to next egg animation frame."""
        self.egg_frame_idx = (self.egg_frame_idx + 1) % config.EGG_FRAME_COUNT
    
    def set_sprite_row(self, row):
        """Set sprite animation row (direction)."""
        self.sprite_row = row % config.SPRITE_ROWS
        self.sprite_frame_idx = 0  # Reset frame when changing animation
    
    def cycle_sprite_row(self):
        """Cycle to next sprite animation row."""
        self.sprite_row = (self.sprite_row + 1) % config.SPRITE_ROWS
    
    # =========================================================================
    # Egg Sprite Rendering
    # =========================================================================
    
    def set_egg(self, color, size):
        """Set the egg variant to display.
        
        Args:
            color: EGG_GREEN, EGG_RED, EGG_BLUE, EGG_YELLOW, or EGG_PINK
            size: EGG_SMALL or EGG_BIG
        """
        self.egg_color = color
        self.egg_size = size
        self.egg_frame_idx = 0
        self.current_egg_frame = -1  # Force redraw on next update
    
    def update_egg(self):
        """Update the egg sprite region if animation frame changed."""
        if self.egg_color is None or self.egg_size is None:
            return
        
        if self.egg_frame_idx != self.current_egg_frame:
            self._update_egg_region(self.egg_color, self.egg_size, self.egg_frame_idx)
            self.current_egg_frame = self.egg_frame_idx
            self.displayed_sprite_type = 'egg'
    
    def _update_egg_region(self, color, size, frame):
        """Redraw the egg sprite region (scaled to display size)."""
        x0 = config.SPRITE_X
        y0 = config.SPRITE_Y
        x1 = x0 + config.SPRITE_DISPLAY_W - 1
        y1 = y0 + config.SPRITE_DISPLAY_H - 1
        
        # Create buffer for the scaled sprite region
        region_w = config.SPRITE_DISPLAY_W
        region_h = config.SPRITE_DISPLAY_H
        region_size = region_w * region_h * config.BPP
        region_buf = bytearray(region_size)
        
        # Copy base frame pixels for this region
        for dy in range(region_h):
            src_y = y0 + dy
            src_row_start = (src_y * config.WIDTH + x0) * config.BPP
            dst_row_start = dy * region_w * config.BPP
            
            for dx in range(region_w):
                si = src_row_start + dx * config.BPP
                di = dst_row_start + dx * config.BPP
                region_buf[di] = self.base_frame[si]
                region_buf[di + 1] = self.base_frame[si + 1]
        
        # Blit scaled egg sprite onto region buffer
        self._blit_egg_to_region_scaled(region_buf, region_w, color, size, frame)
        
        # Push just this region to display
        self.display.block(x0, y0, x1, y1, region_buf)
    
    def _blit_egg_to_region_scaled(self, region_buf, region_w, color, size, frame):
        """Blit egg sprite frame onto region buffer with scaling.
        
        Each source pixel is rendered as a SPRITE_SCALE x SPRITE_SCALE block.
        """
        # Get source coordinates from egg sprite sheet
        sx0, sy0 = config.egg_frame_coords(color, size, frame)
        scale = config.SPRITE_SCALE
        
        for sy in range(config.EGG_SPRITE_H):
            sheet_row_start = ((sy0 + sy) * config.EGG_SHEET_W + sx0) * config.BPP
            
            for sx in range(config.EGG_SPRITE_W):
                si = sheet_row_start + sx * config.BPP
                hi = self.egg_buf[si]
                lo = self.egg_buf[si + 1]
                color_val = (hi << 8) | lo
                if color_val == config.TRANSPARENT_KEY:
                    continue
                
                # Write scale x scale block of pixels
                dst_x = sx * scale
                dst_y = sy * scale
                for by in range(scale):
                    row_start = (dst_y + by) * region_w * config.BPP
                    for bx in range(scale):
                        di = row_start + (dst_x + bx) * config.BPP
                        region_buf[di] = hi
                        region_buf[di + 1] = lo
    
    # =========================================================================
    # Sprite Region Management
    # =========================================================================
    
    def clear_sprite_region(self):
        """Clear the sprite region by restoring from base_frame.
        
        Used when transitioning to a state with no sprite (e.g., PHASE_WAITING).
        """
        x0 = config.SPRITE_X
        y0 = config.SPRITE_Y
        x1 = x0 + config.SPRITE_DISPLAY_W - 1
        y1 = y0 + config.SPRITE_DISPLAY_H - 1
        
        region_w = config.SPRITE_DISPLAY_W
        region_h = config.SPRITE_DISPLAY_H
        region_size = region_w * region_h * config.BPP
        region_buf = bytearray(region_size)
        
        # Copy from base_frame
        for dy in range(region_h):
            src_y = y0 + dy
            src_row_start = (src_y * config.WIDTH + x0) * config.BPP
            dst_row_start = dy * region_w * config.BPP
            
            for dx in range(region_w):
                si = src_row_start + dx * config.BPP
                di = dst_row_start + dx * config.BPP
                region_buf[di] = self.base_frame[si]
                region_buf[di + 1] = self.base_frame[si + 1]
        
        self.display.block(x0, y0, x1, y1, region_buf)
        
        # Reset sprite state
        self.displayed_sprite_type = None
        self.current_egg_frame = -1
        self.egg_color = None
        self.egg_size = None
    
    def _overlay_colorkey(self, dst_buf, src_buf):
        """Apply source buffer onto destination with colorkey transparency."""
        i = 0
        while i < config.BUF_SIZE:
            hi = src_buf[i]
            lo = src_buf[i + 1]
            color = (hi << 8) | lo
            if color != config.TRANSPARENT_KEY:
                dst_buf[i] = hi
                dst_buf[i + 1] = lo
            i += 2
