"""
Safe Touch Screen Handler for Muslim Companion
Handles I2C errors gracefully and provides fallback behavior
"""

import time
from machine import I2C, Pin

class SafeTouch:
    def __init__(self, touch_driver):
        """Initialize safe touch wrapper"""
        self.touch = touch_driver
        self.last_error_time = 0
        self.error_count = 0
        self.max_errors = 5
        self.error_timeout = 5000  # 5 seconds
        self.disabled = False
        
    def get_touch(self):
        """Safely get touch data with error handling"""
        # If touch is disabled due to errors, return None
        if self.disabled:
            # Check if we should try to re-enable
            if time.ticks_diff(time.ticks_ms(), self.last_error_time) > self.error_timeout:
                print("Attempting to re-enable touch...")
                self.disabled = False
                self.error_count = 0
            else:
                return None
        
        try:
            # Attempt to get touch data
            return self.touch.get_touch()
            
        except OSError as e:
            # Handle I2C errors
            if e.errno == 5:  # EIO - Input/Output error
                self.error_count += 1
                self.last_error_time = time.ticks_ms()
                
                if self.error_count >= self.max_errors:
                    print(f"Touch disabled due to {self.error_count} errors")
                    self.disabled = True
                    
                    # Try to reset I2C bus
                    self.try_reset_i2c()
                    
                return None
            else:
                # Re-raise other errors
                raise
                
        except Exception:
            # Silently ignore other errors
            return None
    
    def try_reset_i2c(self):
        """Attempt to reset the I2C bus"""
        try:
            print("Attempting I2C reset...")
            # Try to reinitialize the touch controller
            if hasattr(self.touch, 'init'):
                self.touch.init()
            print("I2C reset attempted")
        except:
            print("I2C reset failed")
    
    def is_working(self):
        """Check if touch is currently working"""
        return not self.disabled