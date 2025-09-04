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
            {'name': 'Location', 'key': 'location_name', 'type': 'text'},
            {'name': 'Calculation Method', 'key': 'method', 'type': 'select', 
             'options': ['ISNA', 'MWL', 'Mecca']},
            {'name': 'Buzzer Enabled', 'key': 'buzzer_enabled', 'type': 'bool'},
            {'name': 'Buzzer Duration', 'key': 'buzzer_duration', 'type': 'number'},
            {'name': 'Display Brightness', 'key': 'display_brightness', 'type': 'number'},
            {'name': 'Time Format', 'key': 'time_format', 'type': 'select', 
             'options': ['12h', '24h']},
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
            
            # Handle joystick navigation
            direction = self.hw.joystick.wait_for_direction(timeout_ms=100)
            
            # Update buttons
            self.hw.buttons.update()
            
            # Check for touch input (for bottom navigation)
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
                    # Handle other touch actions if needed
                    # For now, continue with normal flow for non-tab touches
            
            if direction == 'up':
                selected_index = (selected_index - 1) % len(settings_items)
            elif direction == 'down':
                selected_index = (selected_index + 1) % len(settings_items)
            elif direction == 'right' or self.hw.buttons.get_select_press():
                # Select/modify item
                item = settings_items[selected_index]
                if item['key'] == 'exit':
                    break
                else:
                    self.modify_setting(item)
                    needs_redraw = True  # Redraw after modification
            elif direction == 'left' or self.hw.buttons.get_back_press() or self.hw.joystick.get_button_press():
                # Exit settings
                break
                
            sleep_ms(50)  # Prevent too fast navigation
        
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
            
        elif setting_item['type'] == 'select':
            # Cycle through options
            options = setting_item['options']
            try:
                current_index = options.index(current_value)
                new_index = (current_index + 1) % len(options)
                self.config.set(key, options[new_index])
            except ValueError:
                self.config.set(key, options[0])
                
        elif setting_item['type'] == 'number':
            # Adjust number value
            last_value = current_value
            self.ui.draw_number_editor(setting_item['name'], current_value)
            
            while True:
                direction = self.hw.joystick.wait_for_direction(timeout_ms=100)
                self.hw.buttons.update()
                
                if direction == 'up':
                    current_value += 1
                elif direction == 'down':
                    current_value = max(1, current_value - 1)
                elif direction == 'right' or self.hw.buttons.get_select_press():
                    # Save value
                    self.config.set(key, current_value)
                    break
                elif direction == 'left' or self.hw.buttons.get_back_press() or self.hw.joystick.get_button_press():
                    # Cancel
                    break
                    
                # Only update display if value changed
                if current_value != last_value:
                    self.ui.draw_number_editor(setting_item['name'], current_value)
                    last_value = current_value
                    
                sleep_ms(50)
    
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
            direction = self.hw.joystick.wait_for_direction(timeout_ms=100)
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
                
            sleep_ms(50)
        
        return current_value