"""
Button Driver for GeeekPi GPIO Expansion Module
Handles the two physical buttons with debouncing and feedback
"""

from machine import Pin
import time

class Button:
    def __init__(self, pin_num, pull_up=True, active_low=True):
        """
        Initialize a button
        Args:
            pin_num: GPIO pin number
            pull_up: Use internal pull-up resistor
            active_low: Button is active low (pressed = 0)
        """
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP if pull_up else Pin.PULL_DOWN)
        self.active_low = active_low
        self.last_state = self.pin.value()
        self.pressed = False
        self.released = False
        
        # Debouncing
        self.debounce_time = 50  # ms
        self.last_change_time = 0
        
        # Long press detection
        self.press_start_time = 0
        self.long_press_time = 1000  # ms for long press
        self.long_pressed = False
        
    def _get_state(self):
        """Get current logical state (True = pressed)"""
        raw_state = self.pin.value()
        return not raw_state if self.active_low else raw_state
        
    def update(self):
        """Update button state - call this regularly"""
        current_time = time.ticks_ms()
        current_state = self._get_state()
        
        # Reset flags
        self.pressed = False
        self.released = False
        
        # Debouncing
        if current_state != self.last_state:
            if time.ticks_diff(current_time, self.last_change_time) > self.debounce_time:
                # State actually changed
                if current_state:  # Button pressed
                    self.pressed = True
                    self.press_start_time = current_time
                    self.long_pressed = False
                else:  # Button released
                    self.released = True
                    if time.ticks_diff(current_time, self.press_start_time) >= self.long_press_time:
                        self.long_pressed = True
                
                self.last_state = current_state
                self.last_change_time = current_time
        
    def is_pressed(self):
        """Check if button was just pressed this update"""
        return self.pressed
        
    def is_released(self):
        """Check if button was just released this update"""
        return self.released
        
    def is_held(self):
        """Check if button is currently being held down"""
        return self._get_state()
        
    def is_long_pressed(self):
        """Check if button was long pressed (held > 1 second)"""
        return self.long_pressed
        
    def wait_for_press(self, timeout_ms=None):
        """Wait for button press"""
        start_time = time.ticks_ms()
        
        while True:
            self.update()
            if self.is_pressed():
                return True
                
            if timeout_ms and time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
                return False
                
            time.sleep_ms(10)


class ButtonManager:
    def __init__(self, button1_pin, button2_pin, buzzer_callback=None):
        """
        Initialize button manager for both buttons
        Args:
            button1_pin: GPIO pin for button 1
            button2_pin: GPIO pin for button 2  
            buzzer_callback: Function to call for beep feedback
        """
        self.button1 = Button(button1_pin)
        self.button2 = Button(button2_pin)
        self.buzzer_callback = buzzer_callback
        
        # Button assignments
        self.select_button = self.button1  # Button 1 = Select/OK
        self.back_button = self.button2    # Button 2 = Back/Cancel
        
    def update(self):
        """Update all buttons"""
        self.button1.update()
        self.button2.update()
        
        # Play beep on button press
        if self.buzzer_callback:
            if self.button1.is_pressed():
                self.buzzer_callback(800, 100)  # Select beep
            elif self.button2.is_pressed():
                self.buzzer_callback(600, 150)  # Back beep (lower tone)
                
    def get_select_press(self):
        """Check if select button was pressed"""
        return self.select_button.is_pressed()
        
    def get_back_press(self):
        """Check if back button was pressed"""
        return self.back_button.is_pressed()
        
    def get_select_long_press(self):
        """Check if select button was long pressed"""
        return self.select_button.is_long_pressed()
        
    def get_back_long_press(self):
        """Check if back button was long pressed"""
        return self.back_button.is_long_pressed()
        
    def wait_for_any_button(self, timeout_ms=None):
        """
        Wait for any button press
        Returns: 'select', 'back', or None if timeout
        """
        start_time = time.ticks_ms()
        
        while True:
            self.update()
            
            if self.get_select_press():
                return 'select'
            elif self.get_back_press():
                return 'back'
                
            if timeout_ms and time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
                return None
                
            time.sleep_ms(10)