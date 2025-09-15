"""
Joystick Driver for GeeekPi GPIO Expansion Module
5-way joystick with analog X/Y axes and center push button
"""

from machine import Pin, ADC
import time

class Joystick:
    def __init__(self, x_pin, y_pin, sw_pin, deadzone=200):
        """
        Initialize joystick
        Args:
            x_pin: GPIO pin for X-axis (analog)
            y_pin: GPIO pin for Y-axis (analog) 
            sw_pin: GPIO pin for center button (digital)
            deadzone: Deadzone around center position (0-2048)
        """
        self.x_adc = ADC(Pin(x_pin))
        self.y_adc = ADC(Pin(y_pin))
        self.sw_pin = Pin(sw_pin, Pin.IN, Pin.PULL_UP)
        
        self.deadzone = deadzone
        self.center_x = 32768  # 16-bit ADC center
        self.center_y = 32768
        
        # Calibrate center position
        self.calibrate()
        
        # Button debouncing
        self.last_sw_state = 1
        self.sw_pressed = False
        
    def calibrate(self):
        """Calibrate center position by averaging several readings"""
        print("Calibrating joystick...")
        x_sum = 0
        y_sum = 0
        samples = 10
        
        for _ in range(samples):
            x_sum += self.x_adc.read_u16()
            y_sum += self.y_adc.read_u16()
            time.sleep_ms(10)
            
        self.center_x = x_sum // samples
        self.center_y = y_sum // samples
        print(f"Joystick calibrated: center=({self.center_x}, {self.center_y})")
        
    def read_raw(self):
        """Read raw ADC values"""
        return {
            'x': self.x_adc.read_u16(),
            'y': self.y_adc.read_u16(),
            'sw': self.sw_pin.value()
        }
        
    def read_normalized(self):
        """Read normalized values (-1.0 to 1.0)"""
        raw = self.read_raw()
        
        # Normalize to -1.0 to 1.0 range
        x_norm = (raw['x'] - self.center_x) / 32768.0
        y_norm = (raw['y'] - self.center_y) / 32768.0
        
        # Apply deadzone
        if abs(x_norm) < (self.deadzone / 32768.0):
            x_norm = 0.0
        if abs(y_norm) < (self.deadzone / 32768.0):
            y_norm = 0.0
            
        # Clamp to -1.0 to 1.0
        x_norm = max(-1.0, min(1.0, x_norm))
        y_norm = max(-1.0, min(1.0, y_norm))
        
        return {
            'x': x_norm,
            'y': y_norm,
            'sw': raw['sw']
        }
        
    def get_direction(self, threshold=0.5):
        """
        Get discrete direction from joystick
        Returns: 'up', 'down', 'left', 'right', 'center', or None
        """
        norm = self.read_normalized()
        
        if abs(norm['x']) < threshold and abs(norm['y']) < threshold:
            return 'center'
        elif norm['y'] < -threshold:  # Up (Y-axis inverted)
            return 'up'
        elif norm['y'] > threshold:   # Down
            return 'down'
        elif norm['x'] < -threshold:  # Left
            return 'left' 
        elif norm['x'] > threshold:   # Right
            return 'right'
        else:
            return None
            
    def get_button_press(self):
        """Check for center button press (with debouncing)"""
        current_state = self.sw_pin.value()
        
        if self.last_sw_state == 1 and current_state == 0:
            # Button pressed (falling edge)
            self.sw_pressed = True
            time.sleep_ms(50)  # Debounce delay
        
        self.last_sw_state = current_state
        
        if self.sw_pressed:
            self.sw_pressed = False
            return True
        return False
        
    def wait_for_direction(self, timeout_ms=None):
        """
        Wait for joystick movement in any direction
        Returns the first direction detected or None if timeout
        """
        start_time = time.ticks_ms()
        
        while True:
            direction = self.get_direction()
            if direction and direction != 'center':
                return direction
                
            if timeout_ms and time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
                return None
                
            time.sleep_ms(20)  # Increased sleep for better performance
            
    def wait_for_button(self, timeout_ms=None):
        """
        Wait for center button press
        Returns True if pressed, False if timeout
        """
        start_time = time.ticks_ms()
        
        while True:
            if self.get_button_press():
                return True
                
            if timeout_ms and time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
                return False
                
            time.sleep_ms(10)