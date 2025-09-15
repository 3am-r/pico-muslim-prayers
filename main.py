"""
Muslim Companion Application for Pi Pico 2 WH
Hardware: GeeekPi GPIO Expansion Module with 3.5inch Screen
Display: ST7796 (320x480 pixels)
Touch: GT911 capacitive touch
"""

import time
import gc
from machine import RTC
from time import sleep_ms
# Import from lib folder - boot.py handles path setup
from lib.prayer_times import PrayerTimes
from lib.prayer_settings import PrayerSettings
from lib.simple_settings import SimpleSettings  # Simplified settings for testing
from lib.hijri_calendar import HijriCalendar
from lib.ui_manager import UIManager
from lib.wifi_time_sync import WiFiTimeSync
from hardware_config import get_hardware  # Hardware abstraction
from prayer_config import Config

class MuslimCompanion:
    def __init__(self):
        print("Initializing Muslim Companion Application...")
        
        # Initialize hardware abstraction
        self.hw = get_hardware()
        
        # Get hardware components
        self.display = self.hw.display
        self.touch = self.hw.touch
        self.joystick = self.hw.joystick
        self.buttons = self.hw.buttons
        
        # Get display dimensions
        self.display_width, self.display_height = self.hw.get_display_size()
        
        # Initialize configuration
        self.config = Config()
        
        # Load WiFi configuration if available
        try:
            from wifi_config import configure_wifi
            configure_wifi(self.config)
        except ImportError:
            print("wifi_config.py not found - WiFi features will need manual setup")
        
        # Initialize UI manager
        self.ui = UIManager(self.display, self.touch, self.display_width, self.display_height)
        
        # Initialize prayer times calculator
        self.prayer_calc = PrayerTimes(
            latitude=self.config.get('latitude', 27.9506),  # Default: Tampa
            longitude=self.config.get('longitude', -82.4572),
            timezone=self.config.get('timezone', -5),  # Base timezone without DST
            calculation_method=self.config.get('method', 'ISNA'),
            config=self.config  # Pass config for DST handling
        )
        
        # Initialize settings manager based on touch availability
        if self.touch is None:
            # Use no-touch settings if touch screen failed
            from lib.no_touch_settings import NoTouchSettings
            self.settings_manager = NoTouchSettings(self.ui, self.hw, self.config)
            print("Using No-Touch Settings (touch screen disabled)")
        else:
            # Use simplified settings for debugging
            self.settings_manager = SimpleSettings(self.ui, self.hw, self.config)
            # Original settings manager (uncomment to use)
            # self.settings_manager = PrayerSettings(self.ui, self.hw, self.config)
        
        # Initialize Hijri calendar
        self.hijri_calendar = HijriCalendar()
        
        # Initialize WiFi time sync
        self.wifi_sync = WiFiTimeSync(self.config)
        
        # RTC for time keeping
        self.rtc = RTC()
        
        # Current tab/screen
        self.current_tab = 'prayer'  # 'prayer', 'hijri', 'qibla', 'settings'
        
        # Settings state (for non-blocking settings)
        self.settings_state = {
            'active': False,
            'selected_index': 0,
            'items': []
        }
        
        # Touch debouncing
        self.last_touch_time = 0
        self.touch_debounce_ms = 200  # 200ms debounce
        
        # Performance tracking
        self.last_display_update = 0
        self.display_update_interval = 100  # Minimum ms between display updates
        
        # Sleep mode state
        self.is_sleeping = False
        self.last_activity_time = time.ticks_ms()
        self.sleep_start_time = 0
    
    def format_time(self, time_str, include_seconds=True):
        """Format time string according to user preference (12h/24h)"""
        if not time_str or time_str == '--:--':
            return time_str
            
        time_format = self.config.get('time_format', '12h')
        
        # Parse the time
        parts = time_str.split(':')
        if len(parts) < 2:
            return time_str
            
        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2]) if len(parts) > 2 else 0
        
        if time_format == '12h':
            period = 'AM' if hour < 12 else 'PM'
            if hour == 0:
                hour = 12
            elif hour > 12:
                hour -= 12
            
            if include_seconds and len(parts) > 2:
                return f"{hour}:{minute:02d}:{second:02d} {period}"
            else:
                return f"{hour}:{minute:02d} {period}"
        else:
            # 24-hour format
            if include_seconds and len(parts) > 2:
                return f"{hour:02d}:{minute:02d}:{second:02d}"
            else:
                return f"{hour:02d}:{minute:02d}"
    
    def update_prayer_times(self):
        """Calculate prayer times for current day"""
        return self.prayer_calc.update_prayer_times()
            
    def get_next_prayer(self):
        """Determine the next prayer time"""
        return self.prayer_calc.get_next_prayer()
    
    def handle_input(self):
        """Process all input: touch, buttons, and joystick"""
        # Update button states
        self.buttons.update()
        # Small delay to help with button detection
        time.sleep(0.01)
        
        # Check if any input should wake from sleep
        input_detected = False
        
        # Check legacy settings button (GP12)
        if self.hw.check_legacy_button():
            input_detected = True
            print("Legacy button (GP12) pressed - Opening settings")
            result = self.show_settings()
            if result == True:
                self.update_display()
            elif isinstance(result, str):
                self.switch_tab(result)
            return
        
        # Check joystick for tab navigation (works on all tabs)
        direction = self.joystick.wait_for_direction(timeout_ms=50)  # Short timeout for responsiveness
        if direction:
            input_detected = True
            if direction == 'left':
                # Switch to previous tab
                tabs = ['prayer', 'hijri', 'qibla', 'settings']
                current_index = tabs.index(self.current_tab) if self.current_tab in tabs else 0
                new_index = (current_index - 1) % len(tabs)
                if tabs[new_index] == 'settings':
                    result = self.show_settings()
                    if result == True:
                        self.update_display()
                    elif isinstance(result, str):
                        self.switch_tab(result)
                else:
                    self.switch_tab(tabs[new_index])
                return
            elif direction == 'right':
                # Switch to next tab
                tabs = ['prayer', 'hijri', 'qibla', 'settings']
                current_index = tabs.index(self.current_tab) if self.current_tab in tabs else 0
                new_index = (current_index + 1) % len(tabs)
                if tabs[new_index] == 'settings':
                    result = self.show_settings()
                    if result == True:
                        self.update_display()
                    elif isinstance(result, str):
                        self.switch_tab(result)
                else:
                    self.switch_tab(tabs[new_index])
                return
        
        # Check button 1 for sleep/settings depending on tab
        if self.buttons.get_select_press():
            input_detected = True
            if self.current_tab == 'prayer':
                # On prayer tab, button 1 = sleep
                print("Button 1 (GP14) pressed - Toggling sleep mode")
                if self.is_sleeping:
                    self.wake_from_sleep()
                else:
                    self.enter_sleep_mode()
            else:
                # On other tabs, button 1 = settings
                print("Button 1 (GP14) pressed - Opening settings")
                result = self.show_settings()
                print(f"Settings returned: {result}")
                if result == True:
                    self.update_display()
                elif isinstance(result, str):
                    self.switch_tab(result)
            return
        
        # Check button 2/joystick button for tab-specific actions
        if self.buttons.get_back_press() or self.joystick.get_button_press():
            input_detected = True
            if self.current_tab == 'prayer':
                # Refresh prayer times
                self.update_prayer_times()
                self.update_display()
            elif self.current_tab == 'hijri':
                # Refresh Hijri data
                self.update_display()
            elif self.current_tab == 'qibla':
                # Refresh Qibla compass
                self.update_display()
            return
        
        # Check touch input with debouncing and error handling
        current_time = time.ticks_ms()
        if self.touch and time.ticks_diff(current_time, self.last_touch_time) > self.touch_debounce_ms:
            try:
                touch_data = self.touch.get_touch()
            except OSError as e:
                if e.errno == 5:  # I2C error
                    touch_data = None  # Ignore I2C errors
                else:
                    raise
            except:
                touch_data = None  # Ignore other touch errors
                
            if touch_data:
                input_detected = True
                x, y = touch_data[0], touch_data[1]
                self.last_touch_time = current_time  # Update debounce time
                action_obj = self.ui.handle_touch(x, y)
                
                if action_obj:
                    action = action_obj.get('action') if isinstance(action_obj, dict) else action_obj
                    
                    if action and action.startswith('tab_'):
                        # Tab switching
                        tab_name = action[4:]  # Remove 'tab_' prefix
                        print(f"Main app tab switch request: {tab_name}")  # Debug print
                        if tab_name == 'settings':
                            # Handle settings specially
                            result = self.show_settings()
                            print(f"Settings returned: {result}")  # Debug print
                            if result == True:
                                self.update_display()
                            elif isinstance(result, str):
                                # Switch to requested tab
                                print(f"Switching to tab: {result}")  # Debug print
                                self.switch_tab(result)
                        else:
                            self.switch_tab(tab_name)
                    elif action == 'settings':  # Legacy settings button
                        result = self.show_settings()
                        if result == True:
                            self.update_display()
                        elif isinstance(result, str):
                            # Switch to requested tab
                            self.switch_tab(result)
                    elif action == 'refresh':
                        if self.current_tab == 'prayer':
                            self.update_prayer_times()
                            self.update_display()
                        elif self.current_tab == 'hijri':
                            self.update_display()
                        elif self.current_tab == 'qibla':
                            self.update_display()
        
        # Update activity time if any input was detected
        if input_detected:
            self.update_activity_time()
                
        
    def update_display(self):
        """Update the main display (full redraw)"""
        # Don't update display if sleeping (except when waking up)
        if self.is_sleeping:
            return
            
        _, _, _, _, hour, minute, second, _ = self.rtc.datetime()
        current_time = f"{hour:02d}:{minute:02d}:{second:02d}"
        formatted_current_time = self.format_time(current_time, include_seconds=True)
        
        next_prayer, next_time = self.get_next_prayer()
        formatted_next_time = self.format_time(next_time, include_seconds=False) if next_time else '--:--'
        
        # Format all prayer times
        prayer_times = self.prayer_calc.get_prayer_times()
        formatted_prayer_times = {}
        for prayer, time in prayer_times.items():
            formatted_prayer_times[prayer] = self.format_time(time, include_seconds=False)
        
        if self.current_tab == 'prayer':
            self.ui.draw_main_screen(
                current_time=formatted_current_time,
                prayer_times=formatted_prayer_times,
                next_prayer=next_prayer,
                next_time=formatted_next_time,
                location=self.config.get('location_name', 'Mecca'),
                current_tab=self.current_tab
            )
        elif self.current_tab == 'hijri':
            self.draw_hijri_tab()
        elif self.current_tab == 'qibla':
            self.draw_qibla_tab()
        elif self.current_tab == 'settings':
            # Settings tab is handled by the settings manager in its blocking loop
            # This only runs when first switching to settings
            if not hasattr(self, '_in_settings') or not self._in_settings:
                self._in_settings = True
                result = self.show_settings()
                self._in_settings = False
                print(f"Settings tab returned: {result}")  # Debug print
                if result == True:
                    self.current_tab = 'prayer'  # Return to prayer tab after settings
                elif isinstance(result, str):
                    # Switch to requested tab
                    print(f"Settings requesting switch to: {result}")  # Debug print
                    self.current_tab = result
    
    def update_time_only(self):
        """Update only the time display without redrawing entire screen"""
        # Don't update display if sleeping
        if self.is_sleeping:
            return
            
        _, _, _, _, hour, minute, second, _ = self.rtc.datetime()
        current_time = f"{hour:02d}:{minute:02d}:{second:02d}"
        formatted_current_time = self.format_time(current_time, include_seconds=True)
        
        # Only update the time in the header (only for prayer tab)
        if self.current_tab == 'prayer':
            self.ui.update_time_display(formatted_current_time)
    
    def draw_hijri_tab(self):
        """Draw the Hijri events tab"""
        hijri_date = self.hijri_calendar.get_hijri_date_string()
        next_event, days_until = self.hijri_calendar.get_next_islamic_event()
        
        self.ui.draw_hijri_screen(hijri_date, next_event, days_until, self.current_tab)
    
    def draw_qibla_tab(self):
        """Draw the Qibla compass tab"""
        qibla_direction = self.calculate_qibla_direction()
        location_name = self.config.get('location_name', 'Tampa')
        
        self.ui.draw_qibla_screen(qibla_direction, location_name, self.current_tab)
    
    def calculate_qibla_direction(self):
        """Calculate Qibla direction from current location to Mecca"""
        import math
        
        # Current location coordinates
        lat1 = math.radians(self.config.get('latitude', 27.9506))  # Tampa default
        lon1 = math.radians(self.config.get('longitude', -82.4572))
        
        # Mecca coordinates (Kaaba)
        lat2 = math.radians(21.4225)  # Mecca latitude
        lon2 = math.radians(39.8262)  # Mecca longitude
        
        # Calculate bearing from current location to Mecca
        dlon = lon2 - lon1
        
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360  # Normalize to 0-360 degrees
        
        return bearing
    
    def show_settings(self):
        """Show settings using appropriate method"""
        if hasattr(self.settings_manager, 'show_settings_menu'):
            return self.settings_manager.show_settings_menu()
        else:
            return self.show_settings()
    
    def switch_tab(self, tab_name):
        """Switch to a different tab"""
        print(f"Switching to tab: {tab_name}")  # Debug print
        self.current_tab = tab_name
        self.update_display()
    
    def play_boot_sound(self):
        """Play a startup sound sequence"""
        self.hw.play_boot_sound(self.config.get('buzzer_enabled', True))
    
    def play_prayer_alert(self):
        """Play prayer time alert sound"""
        self.hw.play_prayer_alert(
            self.config.get('buzzer_enabled', True),
            self.config.get('buzzer_duration', 5)
        )
    
    def enter_sleep_mode(self):
        """Enter sleep mode - turn off display"""
        if not self.is_sleeping:
            print("Entering sleep mode")
            self.is_sleeping = True
            self.sleep_start_time = time.ticks_ms()
            # Turn off display by clearing it and turning off backlight if possible
            self.display.clear(0x0000)  # Black screen
            # Note: Actual backlight control would need hardware-specific implementation
    
    def wake_from_sleep(self):
        """Wake from sleep mode - turn on display"""
        if self.is_sleeping:
            print("Waking from sleep mode")
            self.is_sleeping = False
            self.last_activity_time = time.ticks_ms()
            # Refresh the display
            self.update_display()
    
    def update_activity_time(self):
        """Update last activity time (for sleep timeout)"""
        self.last_activity_time = time.ticks_ms()
        # Wake up if we're sleeping and there's activity
        if self.is_sleeping:
            self.wake_from_sleep()
    
    def check_sleep_timeout(self):
        """Check if we should enter sleep mode due to inactivity"""
        if not self.config.get('sleep_mode_enabled', False):
            return
            
        if self.is_sleeping:
            return  # Already sleeping
            
        timeout_ms = self.config.get('sleep_timeout', 30) * 1000
        current_time = time.ticks_ms()
        
        if time.ticks_diff(current_time, self.last_activity_time) > timeout_ms:
            self.enter_sleep_mode()
    
    def check_prayer_time_alert(self, hour, minute, last_check):
        """Check if current time matches any prayer time and trigger alert"""
        current_time = f"{hour:02d}:{minute:02d}"
        
        # Don't alert for the same time twice
        if current_time == last_check:
            return
        
        # Check if it's prayer time
        prayer_name = self.prayer_calc.check_prayer_time_alert(hour, minute)
        if prayer_name:
            print(f"Prayer Alert: It's time for {prayer_name} prayer!")
            
            # Wake from sleep if sleeping (prayer alerts work even when sleeping)
            if self.is_sleeping:
                self.wake_from_sleep()
            
            # Flash the screen to indicate prayer time (works on any tab)
            self.display.fill_rect(0, 0, self.display_width, 60, 0x07E0)  # GREEN
            self.ui.draw_text_centered(f"{prayer_name} Prayer Time!", 20, 3, 0x0000)  # BLACK
            # Play the alert sound
            self.play_prayer_alert()
            # Wait a moment to show the alert
            time.sleep(2)
            # Refresh display after alert to restore current tab
            self.update_display()
            # Reset activity time to prevent immediate sleep after prayer alert
            self.update_activity_time()
        
    def run(self):
        """Main application loop"""
        print("Starting Muslim Companion Application")
        
        # Initial setup
        self.ui.show_splash_screen()
        
        # Play boot sound
        self.play_boot_sound()
        
        time.sleep(2)
        
        # Auto sync time on startup if enabled
        if self.config.get('ntp_on_startup', True) and self.config.get('wifi_ssid'):
            print("Attempting automatic time sync...")
            try:
                if self.wifi_sync.auto_sync_time():
                    print("Startup time sync successful")
                else:
                    print("Startup time sync failed")
            except Exception as e:
                print(f"Startup time sync error: {e}")
        
        self.update_prayer_times()
        
        # Initial full display
        self.update_display()
        
        last_second = -1
        last_minute = -1
        screen_needs_refresh = False
        last_prayer_check = ""  # Track last prayer alert to avoid repeated alerts
        
        while True:
            try:
                _, _, _, _, hour, minute, second, _ = self.rtc.datetime()
                
                # Update time display every second (partial update)
                if second != last_second:
                    self.update_time_only()
                    last_second = second
                    gc.collect()  # Manage memory
                
                # Full screen refresh every minute or when needed
                if minute != last_minute or screen_needs_refresh:
                    self.update_display()
                    last_minute = minute
                    screen_needs_refresh = False
                
                # Check for all input (touch, buttons, joystick)
                self.handle_input()
                
                # Check sleep timeout
                self.check_sleep_timeout()
                
                # Check if it's prayer time (check once per minute)
                if minute != last_minute:
                    current_time_str = f"{hour:02d}:{minute:02d}"
                    self.check_prayer_time_alert(hour, minute, last_prayer_check)
                    last_prayer_check = current_time_str
                
                # Update prayer times at midnight (and refresh screen)
                if hour == 0 and minute == 0 and second == 0:
                    self.update_prayer_times()
                    screen_needs_refresh = True
                
                # Check for scheduled time sync (once per hour at minute 0)
                if minute == 0 and second == 0 and self.config.get('ntp_enabled', True):
                    try:
                        if self.wifi_sync.scheduled_sync():
                            print("Scheduled time sync completed")
                            screen_needs_refresh = True
                    except Exception as e:
                        print(f"Scheduled sync error: {e}")
                
                time.sleep(0.05)  # Reduced for better responsiveness
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)

# Main entry point
if __name__ == "__main__":
    app = MuslimCompanion()
    app.run()