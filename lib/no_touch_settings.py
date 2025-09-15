"""
No-Touch Settings Manager for Muslim Companion
Settings that work with joystick and buttons only (no touch required)
"""

import time
from machine import RTC
from time import sleep_ms

class NoTouchSettings:
    def __init__(self, ui, hw, config):
        """Initialize settings without touch support"""
        self.ui = ui
        self.hw = hw
        self.config = config
        self.rtc = RTC()
        
        # Input debouncing
        self.last_input_time = 0
        self.debounce_ms = 200
        
        print("Settings initialized (Touch disabled)")
        
    def show_settings_menu(self):
        """Show settings using only joystick and buttons"""
        print("=== SETTINGS (No Touch Mode) ===")
        print("Use joystick UP/DOWN to navigate")
        print("Use joystick CENTER or Button 1 to select")
        print("Use Button 2 to exit\n")
        
        settings_items = [
            {'name': 'Buzzer', 'key': 'buzzer_enabled', 'type': 'bool'},
            {'name': 'Time Format', 'key': 'time_format', 'type': 'select', 'options': ['12h', '24h']},
            {'name': 'Daylight Saving', 'key': 'daylight_saving', 'type': 'bool'},
            {'name': 'Exit Settings', 'key': 'exit', 'type': 'action'}
        ]
        
        selected_index = 0
        last_selected = -1
        
        while True:
            # Only redraw if selection changed
            if selected_index != last_selected:
                self.draw_menu(settings_items, selected_index)
                last_selected = selected_index
            
            # Get input
            input_action = self.get_input()
            
            if input_action == 'up':
                selected_index = (selected_index - 1) % len(settings_items)
                print(f"Selected: {settings_items[selected_index]['name']}")
                
            elif input_action == 'down':
                selected_index = (selected_index + 1) % len(settings_items)
                print(f"Selected: {settings_items[selected_index]['name']}")
                
            elif input_action == 'select':
                item = settings_items[selected_index]
                
                if item['key'] == 'exit':
                    print("Exiting settings")
                    break
                    
                # Toggle or modify setting
                self.modify_setting(item)
                
            elif input_action == 'back':
                print("Exiting settings (back button)")
                break
            
            time.sleep(0.05)
        
        return True
    
    def get_input(self):
        """Get input from joystick and buttons only"""
        current_time = time.ticks_ms()
        
        # Debounce check
        if time.ticks_diff(current_time, self.last_input_time) < self.debounce_ms:
            return None
        
        # Check joystick
        try:
            direction = self.hw.joystick.get_direction()
            if direction and direction != 'center':
                self.last_input_time = current_time
                return direction
                
            if self.hw.joystick.get_button_press():
                self.last_input_time = current_time
                return 'select'
        except Exception as e:
            print(f"Joystick error: {e}")
        
        # Check buttons
        try:
            self.hw.buttons.update()
            if self.hw.buttons.get_select_press():
                self.last_input_time = current_time
                return 'select'
            if self.hw.buttons.get_back_press():
                self.last_input_time = current_time
                return 'back'
        except Exception as e:
            print(f"Button error: {e}")
        
        return None
    
    def modify_setting(self, item):
        """Modify a setting value"""
        key = item['key']
        current_value = self.config.get(key)
        
        if item['type'] == 'bool':
            # Toggle boolean
            new_value = not current_value
            self.config.set(key, new_value)
            print(f"{item['name']}: {'ON' if new_value else 'OFF'}")
            
        elif item['type'] == 'select':
            # Cycle through options
            options = item['options']
            try:
                current_index = options.index(current_value)
                new_index = (current_index + 1) % len(options)
                new_value = options[new_index]
                self.config.set(key, new_value)
                print(f"{item['name']}: {new_value}")
            except ValueError:
                self.config.set(key, options[0])
                print(f"{item['name']}: {options[0]}")
    
    def draw_menu(self, items, selected):
        """Draw menu on display"""
        try:
            # Clear display
            self.ui.display.clear(0x0000)
            
            # Draw title
            self.ui.draw_text_centered("Settings", 20, 2, 0xFFFF)
            self.ui.draw_text_centered("(No Touch Mode)", 45, 1, 0xF800)
            
            # Draw menu items
            y_start = 80
            for i, item in enumerate(items):
                y_pos = y_start + i * 40
                
                # Highlight selected item
                if i == selected:
                    self.ui.display.fill_rect(20, y_pos - 5, 280, 35, 0x001F)
                    color = 0xFFFF
                else:
                    color = 0xC618
                
                # Draw item text
                if item['type'] == 'bool':
                    value = self.config.get(item['key'], False)
                    text = f"{item['name']}: {'ON' if value else 'OFF'}"
                elif item['type'] == 'select':
                    value = self.config.get(item['key'], '')
                    text = f"{item['name']}: {value}"
                else:
                    text = item['name']
                
                self.ui.draw_text_centered(text, y_pos + 10, 1, color)
            
            # Draw instructions
            self.ui.draw_text_centered("↑↓ Navigate  ● Select  ← Back", 440, 1, 0xAAAA)
            
        except Exception as e:
            print(f"Drawing error: {e}")