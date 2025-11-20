"""
e-Ink Display Controller - Handles status display and animations.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Optional

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class DisplayController:
    """Controls e-Ink display with status messages and animations."""
    
    def __init__(self, config: dict):
        self.config = config
        self.display_type = config.get('type', 'waveshare_epd')
        self.width = config.get('width', 800)
        self.height = config.get('height', 480)
        self.animation_fps = config.get('animation_fps', 6)
        
        self.current_image: Optional[Image.Image] = None
        self.animation_running = False
        self.animation_thread = None
        
        # Try to initialize display hardware
        self.display = self._init_display()
        
        # Load animation frames if available
        self.animation_frames = self._load_animation_frames()
    
    def _init_display(self):
        """Initialize e-Ink display hardware."""
        try:
            if self.display_type == 'waveshare_epd':
                # Try to import waveshare library
                try:
                    from waveshare_epd import epd7in5_V2
                    display = epd7in5_V2.EPD()
                    display.init()
                    logger.info("Initialized Waveshare e-Ink display")
                    return display
                except ImportError:
                    logger.warning("Waveshare library not available, using mock display")
                    return MockDisplay(self.width, self.height)
            else:
                logger.warning(f"Unknown display type: {self.display_type}, using mock")
                return MockDisplay(self.width, self.height)
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}, using mock")
            return MockDisplay(self.width, self.height)
    
    def _load_animation_frames(self) -> list:
        """Load animation frames from assets directory."""
        frames = []
        assets_dir = Path("/opt/yfitg-scout/assets/animations")
        
        if assets_dir.exists():
            frame_files = sorted(assets_dir.glob("frame_*.png"))
            for frame_file in frame_files:
                try:
                    img = Image.open(frame_file)
                    img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                    frames.append(img)
                except Exception as e:
                    logger.warning(f"Could not load frame {frame_file}: {e}")
        
        # If no frames found, generate simple placeholder frames
        if not frames:
            frames = self._generate_placeholder_frames()
        
        return frames
    
    def _generate_placeholder_frames(self) -> list:
        """Generate simple placeholder animation frames."""
        frames = []
        for i in range(6):
            img = Image.new('1', (self.width, self.height), 255)  # White background
            draw = ImageDraw.Draw(img)
            
            # Draw simple mascot placeholder (circle with magnifying glass)
            center_x, center_y = self.width // 2, self.height // 2
            
            # Body (circle)
            body_radius = 60
            draw.ellipse(
                [center_x - body_radius, center_y - body_radius,
                 center_x + body_radius, center_y + body_radius],
                fill=0
            )
            
            # Magnifying glass (rotating)
            angle = (i * 60) % 360
            glass_size = 40
            glass_x = center_x + int(80 * (i % 3 - 1) * 0.3)
            glass_y = center_y - 30
            
            draw.ellipse(
                [glass_x - glass_size, glass_y - glass_size,
                 glass_x + glass_size, glass_y + glass_size],
                outline=0,
                width=3
            )
            
            # Handle
            draw.line(
                [glass_x + glass_size, glass_y + glass_size,
                 glass_x + glass_size + 20, glass_y + glass_size + 20],
                fill=0,
                width=3
            )
            
            frames.append(img)
        
        return frames
    
    def show_idle(self):
        """Display idle state."""
        self._stop_animation()
        img = self._create_text_image("Ready. Awaiting Consent...")
        self._display_image(img)
    
    def show_scanning(self):
        """Display scanning state with animation."""
        self._start_animation("Scanning...")
    
    def show_processing(self):
        """Display processing state."""
        self._stop_animation()
        img = self._create_text_image("Processing Results...")
        self._display_image(img)
    
    def show_complete(self):
        """Display completion state."""
        self._stop_animation()
        img = self._create_text_image("Scan Complete ✓\nReport Uploaded")
        self._display_image(img)
    
    def show_error(self, message: str = "Error"):
        """Display error state."""
        self._stop_animation()
        img = self._create_text_image(f"Error: {message}\nContact YFITG Support")
        self._display_image(img)
    
    def show_status(self, status: dict):
        """Display current status information."""
        self._stop_animation()
        
        status_text = f"Status: {status.get('status', 'unknown')}\n"
        if 'elapsed_seconds' in status:
            status_text += f"Elapsed: {status['elapsed_seconds']}s\n"
        if 'hosts_scanned' in status:
            status_text += f"Hosts: {status['hosts_scanned']}"
        
        img = self._create_text_image(status_text)
        self._display_image(img)
    
    def update_scan_progress(self, phase: str, percent: float):
        """Update scanning progress display."""
        # Keep animation running, just update caption
        pass  # Could add progress bar overlay
    
    def _create_text_image(self, text: str) -> Image.Image:
        """Create an image with text."""
        img = Image.new('1', (self.width, self.height), 255)  # White
        draw = ImageDraw.Draw(img)
        
        # Try to load font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 32)
            except:
                font = ImageFont.load_default()
        
        # Center text
        lines = text.split('\n')
        y_offset = (self.height - len(lines) * 40) // 2
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (self.width - text_width) // 2
            draw.text((x, y_offset), line, font=font, fill=0)
            y_offset += text_height + 10
        
        return img
    
    def _start_animation(self, caption: str = ""):
        """Start animation loop."""
        if self.animation_running:
            return
        
        self.animation_running = True
        
        def animate():
            frame_delay = 1.0 / self.animation_fps
            frame_index = 0
            
            while self.animation_running and self.animation_frames:
                frame = self.animation_frames[frame_index % len(self.animation_frames)]
                
                # Add caption if provided
                if caption:
                    draw = ImageDraw.Draw(frame)
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
                    except:
                        font = ImageFont.load_default()
                    
                    bbox = draw.textbbox((0, 0), caption, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (self.width - text_width) // 2
                    draw.text((x, self.height - 40), caption, font=font, fill=0)
                
                self._display_image(frame)
                frame_index += 1
                time.sleep(frame_delay)
        
        import threading
        self.animation_thread = threading.Thread(target=animate, daemon=True)
        self.animation_thread.start()
    
    def _stop_animation(self):
        """Stop animation loop."""
        self.animation_running = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1.0)
    
    def _display_image(self, img: Image.Image):
        """Display image on e-Ink screen."""
        try:
            if hasattr(self.display, 'display'):
                # Convert to display format if needed
                if self.display_type == 'waveshare_epd':
                    self.display.display(self.display.getbuffer(img))
                else:
                    self.display.display(img)
            else:
                # Mock display - just log
                logger.debug("Displaying image (mock mode)")
        except Exception as e:
            logger.error(f"Error displaying image: {e}")


class MockDisplay:
    """Mock display for testing without hardware."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        logger.info(f"Mock display initialized: {width}x{height}")
    
    def display(self, img):
        """Mock display - no-op."""
        pass

