"""
GeeekPi GPIO Expansion Module Hardware Configuration
Vendor-specific implementation for GeeekPi 3.5" Display with GPIO expansion
"""

import time
import gc
from machine import Pin, SPI, I2C, RTC

# Import display and touch drivers
from lib.st7796 import ST7796
from lib.gt911 import GT911
from lib.joystick import Joystick
from lib.buttons import ButtonManager

class GeeekPiHardware:
    """
    Hardware abstraction for GeeekPi GPIO Expansion Module
    with 3.5" ST7796 display and GT911 touch controller
    """
    
    # Hardware configuration
    DISPLAY_WIDTH = 320
    DISPLAY_HEIGHT = 480
    
    # ST7796 Display pins (SPI0)
    SPI_CLK = 2   # GP2
    SPI_MOSI = 3  # GP3
    SPI_CS = 5    # GP5
    SPI_DC = 6    # GP6
    SPI_RST = 7   # GP7
    
    # GT911 Touch pins (I2C0)
    I2C_SDA = 8   # GP8
    I2C_SCL = 9   # GP9
    TOUCH_RST = 10  # GP10
    TOUCH_INT = 11  # GP11
    
    # Buzzer pin
    BUZZER_PIN = 13  # GP13
    
    # GeeekPi GPIO Expansion Module pins
    # ADC pins on Pi Pico 2 W: GP26 (ADC0), GP27 (ADC1), GP28 (ADC2)
    JOYSTICK_X = 27   # GP27 (ADC1) - X axis
    JOYSTICK_Y = 26   # GP26 (ADC0) - Y axis 
    JOYSTICK_SW = 22  # GP22 (joystick center button - separate from button 2)
    BUTTON_1 = 14     # GP14 (select/OK button)
    BUTTON_2 = 15     # GP15 (back/cancel button)
    
    # Additional pins for future use
    RGB_LED = 12      # GP12 (RGB LED)
    BLUE_LED_1 = 16   # GP16 (Blue LED)
    BLUE_LED_2 = 17   # GP17 (Blue LED)
    
    # Legacy settings button (for backward compatibility)
    SETTINGS_BUTTON = 12  # GP12 (now used for RGB LED)
    
    def __init__(self):
        """Initialize all hardware components"""
        print("Initializing GeeekPi Hardware...")
        
        # Initialize display
        self.spi = SPI(0, baudrate=40000000, polarity=0, phase=0,
                      sck=Pin(self.SPI_CLK), mosi=Pin(self.SPI_MOSI))
        self.display = ST7796(self.spi, cs=Pin(self.SPI_CS, Pin.OUT),
                              dc=Pin(self.SPI_DC, Pin.OUT),
                              rst=Pin(self.SPI_RST, Pin.OUT),
                              width=self.DISPLAY_WIDTH, height=self.DISPLAY_HEIGHT)
        
        # Initialize touch screen with error handling
        try:
            self.i2c = I2C(0, scl=Pin(self.I2C_SCL), sda=Pin(self.I2C_SDA), freq=400000)
            self.touch = GT911(self.i2c, rst=Pin(self.TOUCH_RST, Pin.OUT),
                               int_pin=Pin(self.TOUCH_INT, Pin.IN))
            print("Touch screen initialized")
        except Exception as e:
            print(f"Touch screen initialization failed: {e}")
            self.touch = None  # Set to None if initialization fails
        
        # Initialize buzzer
        self.buzzer = Pin(self.BUZZER_PIN, Pin.OUT)
        
        # Initialize joystick
        self.joystick = Joystick(self.JOYSTICK_X, self.JOYSTICK_Y, self.JOYSTICK_SW)
        
        # Initialize buttons with buzzer callback
        self.buttons = ButtonManager(self.BUTTON_1, self.BUTTON_2, 
                                    buzzer_callback=self.play_tone)
        
        # Initialize legacy settings button (if using RGB LED pin as button)
        self.settings_button = Pin(self.SETTINGS_BUTTON, Pin.IN, Pin.PULL_UP)
        self.last_button_state = 1
        self.button_pressed = False
        
        # Initialize LEDs (optional, for future use)
        self.blue_led_1 = Pin(self.BLUE_LED_1, Pin.OUT)
        self.blue_led_2 = Pin(self.BLUE_LED_2, Pin.OUT)
        self.blue_led_1.off()
        self.blue_led_2.off()
        
    def play_tone(self, frequency, duration_ms):
        """Play a tone at specified frequency for specified duration"""
        if frequency == 0:
            time.sleep(duration_ms / 1000)
            return
            
        period = 1000000 // frequency  # Period in microseconds
        cycles = (duration_ms * 1000) // period
        
        for _ in range(cycles):
            self.buzzer.on()
            time.sleep_us(period // 2)
            self.buzzer.off()
            time.sleep_us(period // 2)
    
    def play_boot_sound(self, enabled=True):
        """Play a startup sound sequence"""
        if enabled:
            # Play three ascending beeps
            frequencies = [800, 1000, 1200]  # Hz
            for freq in frequencies:
                self.play_tone(freq, 200)  # 200ms each
                time.sleep(0.05)  # 50ms gap
    
    def play_prayer_alert(self, enabled=True, duration=5):
        """Play prayer time alert sound"""
        if enabled:
            # Play a gentle prayer alert tone
            for _ in range(duration):
                self.play_tone(1000, 500)  # 1kHz for 500ms
                time.sleep(0.5)  # 500ms silence
    
    def check_legacy_button(self):
        """Check legacy settings button state"""
        current_button_state = self.settings_button.value()
        if self.last_button_state == 1 and current_button_state == 0:
            self.button_pressed = True
            time.sleep(0.05)  # Debounce
        self.last_button_state = current_button_state
        
        if self.button_pressed:
            self.button_pressed = False
            return True
        return False
    
    def get_display_size(self):
        """Return display dimensions"""
        return self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT
    
    def cleanup(self):
        """Cleanup hardware resources"""
        # Turn off LEDs
        self.blue_led_1.off()
        self.blue_led_2.off()
        # Turn off buzzer
        self.buzzer.off()
        print("GeeekPi Hardware cleaned up")