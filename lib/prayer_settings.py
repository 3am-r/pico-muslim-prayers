"""
Settings Manager for Muslim Companion Application
Handles all settings-related functionality
"""

from time import sleep_ms
from machine import RTC

class PrayerSettings:
    def __init__(self, ui, hw, config):
        """Initialize settings manager"""
        self.ui = ui
        self.hw = hw
        self.config = config
        self.rtc = RTC()
        
    def show_settings_with_navigation(self):
        """Display settings screen with joystick navigation"""
        settings_items = [
            {'name': 'Set Clock Time', 'key': 'set_clock', 'type': 'clock'},
            {'name': 'WiFi Setup', 'key': 'wifi_setup', 'type': 'action'},
            {'name': 'Sync Time Now', 'key': 'sync_time', 'type': 'action'},
            {'name': 'Location', 'key': 'location_name', 'type': 'text'},
            {'name': 'Calculation Method', 'key': 'method', 'type': 'select', 
             'options': ['ISNA', 'MWL', 'Mecca']},
            {'name': 'Daylight Saving', 'key': 'daylight_saving', 'type': 'bool'},
            {'name': 'Buzzer Enabled', 'key': 'buzzer_enabled', 'type': 'bool'},
            {'name': 'Buzzer Duration', 'key': 'buzzer_duration', 'type': 'number'},
            {'name': 'Display Brightness', 'key': 'display_brightness', 'type': 'number'},
            {'name': 'Time Format', 'key': 'time_format', 'type': 'select', 
             'options': ['12h', '24h']},
            {'name': 'Auto Time Sync', 'key': 'ntp_enabled', 'type': 'bool'},
            {'name': 'Exit Settings', 'key': 'exit', 'type': 'action'}
        ]
        
        selected_index = 0
        last_selected_index = -1  # Track if selection changed
        needs_redraw = True  # Initial draw needed
        
        while True:
            # Only draw if something changed
            if needs_redraw or selected_index != last_selected_index:
                self.ui.draw_settings_menu(settings_items, selected_index, self.config)
                last_selected_index = selected_index
                needs_redraw = False
            
            # Handle joystick navigation - reduced timeout for responsiveness
            direction = self.hw.joystick.wait_for_direction(timeout_ms=50)
            
            # Update buttons
            self.hw.buttons.update()
            
            # Check for touch input - less frequent to improve performance
            if self.hw.touch:  # Only if touch is available
                touch_data = self.hw.touch.get_touch()
                if touch_data:
                    x, y = touch_data[0], touch_data[1]
                    action_obj = self.ui.handle_touch(x, y)
                    
                    if action_obj:
                        action = action_obj.get('action') if isinstance(action_obj, dict) else action_obj
                        
                        if action and action.startswith('tab_'):
                            # Tab switching from settings
                            tab_name = action[4:]  # Remove 'tab_' prefix
                            if tab_name != 'settings':
                                # Switch to different tab
                                return tab_name  # Return the tab to switch to
                            # If same tab (settings), just continue
            
            if direction == 'up':
                selected_index = (selected_index - 1) % len(settings_items)
            elif direction == 'down':
                selected_index = (selected_index + 1) % len(settings_items)
            elif direction == 'right' or self.hw.buttons.get_select_press():
                # Select/modify item
                item = settings_items[selected_index]
                if item['key'] == 'exit':
                    break
                elif item['key'] == 'wifi_setup':
                    self.setup_wifi()
                    needs_redraw = True
                elif item['key'] == 'sync_time':
                    self.sync_time_now()
                    needs_redraw = True
                else:
                    result = self.modify_setting(item)
                    needs_redraw = True  # Redraw after modification
                    # If DST setting was changed, update prayer times
                    if item['key'] == 'daylight_saving' and result:
                        # Force prayer times recalculation
                        self.config.set('last_prayer_update', 0)
            elif direction == 'left' or self.hw.buttons.get_back_press() or self.hw.joystick.get_button_press():
                # Exit settings
                break
                
            sleep_ms(20)  # Reduced sleep for better responsiveness
        
        # Return to main screen (just redraw, don't recalculate prayer times)
        return True  # Signal to update display
    
    def modify_setting(self, setting_item):
        """Modify a setting using joystick/buttons"""
        key = setting_item['key']
        
        if key == 'set_clock':
            self.set_clock_time()
            return
            
        current_value = self.config.get(key)
        
        if setting_item['type'] == 'bool':
            # Toggle boolean
            new_value = not current_value
            self.config.set(key, new_value)
            
            # Show DST status if this is the daylight saving setting
            if key == 'daylight_saving':
                self.show_dst_status(new_value)
            
            return True
            
        elif setting_item['type'] == 'select':
            # Cycle through options
            options = setting_item['options']
            try:
                current_index = options.index(current_value)
                new_index = (current_index + 1) % len(options)
                self.config.set(key, options[new_index])
            except ValueError:
                self.config.set(key, options[0])
            return True
                
        elif setting_item['type'] == 'number':
            # Adjust number value
            last_value = current_value
            self.ui.draw_number_editor(setting_item['name'], current_value)
            
            while True:
                direction = self.hw.joystick.wait_for_direction(timeout_ms=30)  # Faster response
                self.hw.buttons.update()
                
                if direction == 'up':
                    current_value += 1
                elif direction == 'down':
                    current_value = max(1, current_value - 1)
                elif direction == 'right' or self.hw.buttons.get_select_press():
                    # Save value
                    self.config.set(key, current_value)
                    return True
                elif direction == 'left' or self.hw.buttons.get_back_press() or self.hw.joystick.get_button_press():
                    # Cancel
                    return False
                    
                # Only update display if value changed
                if current_value != last_value:
                    self.ui.draw_number_editor(setting_item['name'], current_value)
                    last_value = current_value
                    
                sleep_ms(20)  # Faster loop
    
    def set_clock_time(self):
        """Set the RTC clock time"""
        # Get current time
        year, month, day, weekday, hour, minute, second, _ = self.rtc.datetime()
        
        # Edit hour
        hour = self.edit_time_value("Hour", hour, 0, 23)
        if hour is None:
            return  # Cancelled
            
        # Edit minute
        minute = self.edit_time_value("Minute", minute, 0, 59)
        if minute is None:
            return  # Cancelled
            
        # Edit day
        day = self.edit_time_value("Day", day, 1, 31)
        if day is None:
            return  # Cancelled
            
        # Edit month
        month = self.edit_time_value("Month", month, 1, 12)
        if month is None:
            return  # Cancelled
            
        # Edit year
        year = self.edit_time_value("Year", year, 2024, 2050)
        if year is None:
            return  # Cancelled
            
        # Set the new time
        self.rtc.datetime((year, month, day, weekday, hour, minute, 0, 0))
        print(f"Clock set to: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
        
        # Show confirmation
        self.ui.display.fill_rect(50, 200, 220, 80, 0x07E0)  # Green background
        self.ui.draw_text_centered("Clock Time Set!", 220, 2, 0x0000)
        sleep_ms(1000)
    
    def edit_time_value(self, name, current_value, min_val, max_val):
        """Edit a time value (hour, minute, day, month, year)"""
        last_value = current_value
        self.ui.draw_number_editor(f"Set {name}", current_value)
        
        while True:
            direction = self.hw.joystick.wait_for_direction(timeout_ms=30)  # Faster response
            self.hw.buttons.update()
            
            if direction == 'up':
                current_value = min(max_val, current_value + 1)
            elif direction == 'down':
                current_value = max(min_val, current_value - 1)
            elif direction == 'right' or self.hw.buttons.get_select_press():
                # Save value
                return current_value
            elif direction == 'left' or self.hw.buttons.get_back_press() or self.hw.joystick.get_button_press():
                # Cancel
                return None
                
            # Only update display if value changed
            if current_value != last_value:
                self.ui.draw_number_editor(f"Set {name}", current_value)
                last_value = current_value
                
            sleep_ms(20)  # Faster loop
        
        return current_value
    
    def setup_wifi(self):
        """WiFi setup wizard"""
        # Import WiFi module
        try:
            from lib.wifi_time_sync import WiFiTimeSync
            wifi_sync = WiFiTimeSync(self.config)
        except ImportError:
            self.show_message("WiFi module not available")
            return
            
        # Show WiFi setup screen
        self.ui.display.fill(0x0000)  # Clear screen
        self.ui.draw_text_centered("WiFi Setup", 50, 3, 0xFFFF)
        self.ui.draw_text_centered("Enter WiFi credentials", 80, 1, 0xFFFF)
        
        # Simple WiFi setup - for demo purposes
        # In a real implementation, you'd want a proper text input interface
        current_ssid = self.config.get('wifi_ssid', '')
        current_password = self.config.get('wifi_password', '')
        
        if current_ssid:
            self.ui.draw_text_centered(f"Current: {current_ssid}", 120, 1, 0x07E0)
            self.ui.draw_text_centered("Press RIGHT to test", 160, 1, 0xFFFF)
            self.ui.draw_text_centered("Press LEFT to exit", 180, 1, 0xFFFF)
            
            while True:
                direction = self.hw.joystick.wait_for_direction(timeout_ms=30)
                self.hw.buttons.update()
                
                if direction == 'right' or self.hw.buttons.get_select_press():
                    # Test connection
                    self.ui.draw_text_centered("Testing connection...", 220, 1, 0xFFE0)
                    if wifi_sync.connect_wifi():
                        self.ui.draw_text_centered("WiFi Connected!", 240, 2, 0x07E0)
                        sleep_ms(1500)  # Reduced wait time
                        wifi_sync.disconnect_wifi()
                    else:
                        self.ui.draw_text_centered("Connection Failed!", 240, 2, 0xF800)
                        sleep_ms(1500)  # Reduced wait time
                    break
                elif direction == 'left' or self.hw.buttons.get_back_press():
                    break
                    
                sleep_ms(20)
        else:
            self.ui.draw_text_centered("No WiFi configured", 120, 1, 0xF800)
            self.ui.draw_text_centered("Configure in code", 140, 1, 0xFFFF)
            self.ui.draw_text_centered("Press any key to exit", 180, 1, 0xFFFF)
            
            while True:
                direction = self.hw.joystick.wait_for_direction(timeout_ms=30)
                self.hw.buttons.update()
                
                if direction or self.hw.buttons.get_select_press() or self.hw.buttons.get_back_press():
                    break
                sleep_ms(20)
    
    def sync_time_now(self):
        """Manually sync time with NTP"""
        try:
            from lib.wifi_time_sync import WiFiTimeSync
            wifi_sync = WiFiTimeSync(self.config)
        except ImportError:
            self.show_message("WiFi module not available")
            return
            
        # Show sync screen
        self.ui.display.fill(0x0000)  # Clear screen
        self.ui.draw_text_centered("Syncing Time...", 100, 3, 0xFFFF)
        
        if self.config.get('wifi_ssid'):
            self.ui.draw_text_centered("Connecting to WiFi...", 140, 1, 0xFFE0)
            
            if wifi_sync.auto_sync_time():
                self.ui.draw_text_centered("Time Synchronized!", 180, 2, 0x07E0)
                # Show new time
                year, month, day, weekday, hour, minute, second, _ = self.rtc.datetime()
                time_str = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
                self.ui.draw_text_centered(time_str, 220, 1, 0xFFFF)
            else:
                self.ui.draw_text_centered("Sync Failed!", 180, 2, 0xF800)
                self.ui.draw_text_centered("Check WiFi settings", 210, 1, 0xFFFF)
        else:
            self.ui.draw_text_centered("No WiFi configured", 140, 1, 0xF800)
            self.ui.draw_text_centered("Setup WiFi first", 170, 1, 0xFFFF)
        
        sleep_ms(3000)  # Show result for 3 seconds
    
    def show_message(self, message):
        """Show a simple message"""
        self.ui.display.fill(0x0000)
        self.ui.draw_text_centered(message, 150, 2, 0xFFFF)
        sleep_ms(2000)
    
    def show_dst_status(self, enabled):
        """Show daylight saving time status"""
        try:
            from lib.dst_utils import get_current_timezone_offset, format_timezone_display
            
            base_timezone = self.config.get('timezone', -5)
            current_offset = get_current_timezone_offset(base_timezone, enabled)
            timezone_display = format_timezone_display(base_timezone, enabled)
            
            # Show status
            self.ui.display.fill(0x0000)
            self.ui.draw_text_centered("Daylight Saving Time", 80, 2, 0xFFFF)
            
            if enabled:
                self.ui.draw_text_centered("ENABLED", 120, 3, 0x07E0)  # Green
            else:
                self.ui.draw_text_centered("DISABLED", 120, 3, 0xF800)  # Red
            
            self.ui.draw_text_centered(f"Timezone: {timezone_display}", 180, 1, 0xFFFF)
            
            # Show base vs current timezone if different
            if current_offset != base_timezone:
                self.ui.draw_text_centered(f"Base: UTC{base_timezone:+d}", 210, 1, 0xAAAA)
                self.ui.draw_text_centered(f"Current: UTC{current_offset:+d}", 230, 1, 0x07E0)
            
            sleep_ms(2000)  # Reduced to 2 seconds for better responsiveness
            
        except ImportError:
            self.show_message("DST utils not available")