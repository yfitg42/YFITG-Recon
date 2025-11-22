"""
GPIO Button Handler - Manages red push button interactions.
"""

import logging
import threading
import time

logger = logging.getLogger(__name__)

# Try to import RPi.GPIO, fallback to mock for development
GPIO_AVAILABLE = False
GPIO = None
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, Exception) as e:
    # Catch all exceptions including Jetson.GPIO initialization errors
    GPIO_AVAILABLE = False
    GPIO = None
    logger.warning(f"RPi.GPIO not available ({type(e).__name__}: {e}), using mock GPIO")


class ButtonHandler:
    """Handles GPIO button press events."""
    
    def __init__(
        self,
        config: dict,
        on_short_press: callable = None,
        on_long_press: callable = None
    ):
        self.gpio_pin = config.get('gpio_pin', 18)
        self.long_press_duration = config.get('long_press_duration', 3.0)
        self.on_short_press = on_short_press
        self.on_long_press = on_long_press
        
        self.press_start_time = None
        self.monitoring = False
        self.monitor_thread = None
        
        if GPIO_AVAILABLE:
            self._setup_gpio()
        else:
            logger.warning("GPIO not available, button handler disabled")
    
    def _setup_gpio(self):
        """Configure GPIO pin for button input."""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            logger.info(f"GPIO pin {self.gpio_pin} configured for button input")
        except Exception as e:
            logger.error(f"Failed to setup GPIO: {e}")
            # Disable GPIO if setup fails
            global GPIO_AVAILABLE
            GPIO_AVAILABLE = False
    
    def start(self):
        """Start monitoring button presses."""
        if not GPIO_AVAILABLE:
            return
        
        self.monitoring = True
        
        def monitor():
            while self.monitoring:
                try:
                    # Read button state (LOW when pressed, HIGH when released)
                    button_state = GPIO.input(self.gpio_pin)
                    
                    if button_state == GPIO.LOW:  # Button pressed
                        if self.press_start_time is None:
                            self.press_start_time = time.time()
                            logger.debug("Button pressed")
                    
                    else:  # Button released
                        if self.press_start_time is not None:
                            press_duration = time.time() - self.press_start_time
                            
                            if press_duration >= self.long_press_duration:
                                logger.info(f"Long press detected ({press_duration:.1f}s)")
                                if self.on_long_press:
                                    self.on_long_press()
                            else:
                                logger.info(f"Short press detected ({press_duration:.1f}s)")
                                if self.on_short_press:
                                    self.on_short_press()
                            
                            self.press_start_time = None
                    
                    time.sleep(0.1)  # Poll every 100ms
                
                except Exception as e:
                    logger.error(f"Error monitoring button: {e}")
                    time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
        logger.info("Button monitoring started")
    
    def stop(self):
        """Stop monitoring button presses."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup(self.gpio_pin)
            except:
                pass

