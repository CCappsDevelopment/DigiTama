# graphics.py
# Graphics rendering: asset loading, compositing, sprite blitting

import config


class Graphics:
    """Handles all rendering operations."""
    
    def __init__(self, display):
        self.display = display
        
        # Cached assets (loaded once)
        self.menu_buf = None
        self.sprite_buf = None
        self.cached_bg = None  # Single cached background frame
        
        # Animation state
        self.bg_frame_idx = 0
        self.sprite_frame_idx = 0
        self.sprite_row = 0  # 0=forward, 1=left, 2=right, 3=back
    
    def load_assets(self):
        """Load all static assets into memory."""
        print("Loading assets...")
        
        # Menu overlay only - testing for responsiveness
        self.menu_buf = self._load_raw(
            config.ASSET_MENU, 
            config.BUF_SIZE
        )
        
        print("Assets loaded")
    
    def _load_raw(self, path, expected_size):
        """Load a raw RGB565 file."""
        with open(path, "rb") as f:
            data = f.read()
        if len(data) != expected_size:
            raise ValueError(f"Unexpected size for {path}: {len(data)}")
        return bytearray(data)
    
    def load_bg_frame(self, index):
        """Load a background frame by index."""
        fname = config.ASSET_BG_FRAMES[index]
        return self._load_raw(fname, config.BUF_SIZE)
    
    def render_frame(self, selected_menu=None):
        """Render a complete frame and push to display.
        
        Args:
            selected_menu: Index of selected menu item (0-9) or None
            
        Returns:
            The frame buffer (for potential further manipulation)
        """
        # Just copy the menu buffer directly (no bg, no sprite)
        frame = bytearray(self.menu_buf)
        
        # Apply menu selection highlight
        if selected_menu is not None:
            self._invert_rect(frame, config.MENU_RECTS[selected_menu])
        
        # Push to display
        self.display.block(0, 0, config.WIDTH - 1, config.HEIGHT - 1, frame)
        
        return frame
    
    def advance_sprite_frame(self):
        """Advance to next sprite animation frame."""
        self.sprite_frame_idx = (self.sprite_frame_idx + 1) % config.SPRITE_FRAMES_PER_ROW
    
    def set_sprite_row(self, row):
        """Set sprite animation row (direction)."""
        self.sprite_row = row % config.SPRITE_ROWS
    
    def cycle_sprite_row(self):
        """Cycle to next sprite animation row."""
        self.sprite_row = (self.sprite_row + 1) % config.SPRITE_ROWS
    
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
    
    def _invert_rect(self, buf, rect):
        """Invert colors in a rectangle (for selection highlight)."""
        x0, y0, x1, y1 = rect
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(config.WIDTH - 1, x1)
        y1 = min(config.HEIGHT - 1, y1)
        
        for y in range(y0, y1 + 1):
            row_start = (y * config.WIDTH + x0) * config.BPP
            for x in range(x0, x1 + 1):
                i = row_start + (x - x0) * config.BPP
                hi = buf[i]
                lo = buf[i + 1]
                c = (hi << 8) | lo
                c ^= 0xFFFF
                buf[i] = (c >> 8) & 0xFF
                buf[i + 1] = c & 0xFF
    
    def _blit_sprite(self, frame_buf, anim_row, frame_index):
        """Blit one sprite frame onto the frame buffer."""
        sx0 = config.SPRITE_W * frame_index
        sy0 = config.SPRITE_H * anim_row
        
        for dy in range(config.SPRITE_H):
            sy = sy0 + dy
            sheet_row_start = (sy * config.SPRITE_SHEET_W + sx0) * config.BPP
            
            dst_y = config.SPRITE_Y + dy
            frame_row_start = (dst_y * config.WIDTH + config.SPRITE_X) * config.BPP
            
            for dx in range(config.SPRITE_W):
                si = sheet_row_start + dx * config.BPP
                hi = self.sprite_buf[si]
                lo = self.sprite_buf[si + 1]
                color = (hi << 8) | lo
                if color == config.TRANSPARENT_KEY:
                    continue
                di = frame_row_start + dx * config.BPP
                frame_buf[di] = hi
                frame_buf[di + 1] = lo
