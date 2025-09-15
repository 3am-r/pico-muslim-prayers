"""
Simplified Settings Manager for Muslim Companion
Robust input handling without complex UI blocking
"""

import time
from machine import RTC
from time import sleep_ms

class SimpleSettings:
    def __init__(self, ui, hw, config):
        """Initialize simple settings manager"""
        self.ui = ui
        self.hw = hw
        self.config = config
        self.rtc = RTC()
        
        # Input debouncing
        self.last_input_time = 0
        self.debounce_ms = 150
        
    def show_settings_menu(self):
        """Show settings with reliable input handling"""
        print("=== ENTERING SETTINGS ===")
        
        # Verify hardware is accessible (only print once)
        try:
            joystick_ok = self.hw.joystick is not None
            touch_ok = self.hw.touch is not None
            buttons_ok = self.hw.buttons is not None
            
            if not joystick_ok or not buttons_ok:
                print(f"Hardware status - Joystick: {joystick_ok}, Touch: {touch_ok}, Buttons: {buttons_ok}")
        except Exception as e:
            print(f"Hardware access error: {e}")
            return True
        
        settings_items = [
            "Set Clock Time",
            "WiFi Setup",
            "Sync Time Now",
            "Location: " + self.config.get('location_name', 'Tampa'),
            "Calc Method: " + self.config.get('method', 'ISNA'),
            "Daylight Saving: " + ("ON" if self.config.get('daylight_saving', True) else "OFF"),
            "Buzzer: " + ("ON" if self.config.get('buzzer_enabled', True) else "OFF"),
            "Buzzer Duration: " + str(self.config.get('buzzer_duration', 5)) + "s",
            "Time Format: " + self.config.get('time_format', '12h'),
            "Auto Time Sync: " + ("ON" if self.config.get('ntp_enabled', True) else "OFF"),
            "Sleep Mode: " + ("ON" if self.config.get('sleep_mode_enabled', False) else "OFF"),
            "Sleep Timeout: " + str(self.config.get('sleep_timeout', 30)) + "s",
            "Exit Settings"
        ]
        
        selected_index = 0
        last_selected_index = -1  # Track changes
        needs_redraw = True  # Initial draw needed
        
        while True:
            # Only draw if something changed
            if needs_redraw or selected_index != last_selected_index:
                try:
                    self.draw_simple_menu(settings_items, selected_index)
                    last_selected_index = selected_index
                    needs_redraw = False
                except Exception as e:
                    print(f"Drawing error: {e}")
            
            # Handle input with timeout
            input_result = self.wait_for_input(timeout_ms=100)
            
            if input_result == 'up':
                selected_index = (selected_index - 1) % len(settings_items)
                # Don't print every selection change - causes console spam
                
            elif input_result == 'down':
                selected_index = (selected_index + 1) % len(settings_items)
                # Don't print every selection change - causes console spam
                
            elif input_result == 'left':
                # Navigate to previous tab (hijri)
                print("Switching to Hijri tab")
                return 'hijri'
                
            elif input_result == 'right':
                # Navigate to next tab (prayer)
                print("Switching to Prayer tab")
                return 'prayer'
                
            elif input_result == 'select':
                print(f"Settings: Selecting item {selected_index}: {settings_items[selected_index]}")
                # Handle different settings
                
                if selected_index == 0:  # Set Clock Time
                    print("Clock setting not yet implemented in simple mode")
                    
                elif selected_index == 1:  # WiFi Setup
                    self.show_wifi_setup()
                    needs_redraw = True
                    
                elif selected_index == 2:  # Sync Time Now
                    self.sync_time_now()
                    needs_redraw = True
                    
                elif selected_index == 3:  # Location
                    # Cycle through US cities
                    cities = self.config.get_us_cities()
                    current = self.config.get('location_name', 'Tampa')
                    
                    # Find current city
                    current_idx = 0
                    for i, city in enumerate(cities):
                        if city['name'] == current:
                            current_idx = i
                            break
                    
                    # Select next city
                    new_idx = (current_idx + 1) % len(cities)
                    new_city = cities[new_idx]
                    
                    # Update location with all data
                    self.config.update_location(new_city)
                    settings_items[3] = f"Location: {new_city['name']}"
                    needs_redraw = True
                    print(f"Location changed to {new_city['name']}")
                    
                elif selected_index == 4:  # Calc Method
                    methods = ['ISNA', 'MWL', 'Mecca']
                    current = self.config.get('method', 'ISNA')
                    try:
                        idx = methods.index(current)
                        new_method = methods[(idx + 1) % len(methods)]
                    except:
                        new_method = methods[0]
                    self.config.set('method', new_method)
                    settings_items[4] = f"Calc Method: {new_method}"
                    needs_redraw = True
                    
                elif selected_index == 5:  # Daylight Saving
                    current = self.config.get('daylight_saving', True)
                    self.config.set('daylight_saving', not current)
                    settings_items[5] = "Daylight Saving: " + ("ON" if not current else "OFF")
                    needs_redraw = True
                    
                elif selected_index == 6:  # Buzzer
                    current = self.config.get('buzzer_enabled', True)
                    self.config.set('buzzer_enabled', not current)
                    settings_items[6] = "Buzzer: " + ("ON" if not current else "OFF")
                    needs_redraw = True
                    
                elif selected_index == 7:  # Buzzer Duration
                    current = self.config.get('buzzer_duration', 5)
                    new_duration = current + 1 if current < 10 else 1
                    self.config.set('buzzer_duration', new_duration)
                    settings_items[7] = f"Buzzer Duration: {new_duration}s"
                    needs_redraw = True
                    
                elif selected_index == 8:  # Time Format
                    current = self.config.get('time_format', '12h')
                    new_format = '24h' if current == '12h' else '12h'
                    self.config.set('time_format', new_format)
                    settings_items[8] = f"Time Format: {new_format}"
                    needs_redraw = True
                    
                elif selected_index == 9:  # Auto Time Sync
                    current = self.config.get('ntp_enabled', True)
                    self.config.set('ntp_enabled', not current)
                    settings_items[9] = "Auto Time Sync: " + ("ON" if not current else "OFF")
                    needs_redraw = True
                    
                elif selected_index == 10:  # Sleep Mode
                    current = self.config.get('sleep_mode_enabled', False)
                    self.config.set('sleep_mode_enabled', not current)
                    settings_items[10] = "Sleep Mode: " + ("ON" if not current else "OFF")
                    needs_redraw = True
                    
                elif selected_index == 11:  # Sleep Timeout
                    current = self.config.get('sleep_timeout', 30)
                    # Cycle through timeouts: 10, 30, 60, 120, 300 seconds
                    timeouts = [10, 30, 60, 120, 300]
                    try:
                        idx = timeouts.index(current)
                        new_timeout = timeouts[(idx + 1) % len(timeouts)]
                    except:
                        new_timeout = timeouts[0]
                    self.config.set('sleep_timeout', new_timeout)
                    settings_items[11] = f"Sleep Timeout: {new_timeout}s"
                    needs_redraw = True
                    
                elif selected_index == 12:  # Exit
                    print("Exiting settings")
                    break
                    
            elif input_result == 'exit':
                print("Exiting settings")
                break
                
            elif input_result == 'tab_prayer':
                return 'prayer'
            elif input_result == 'tab_hijri':
                return 'hijri'
                
        return True
    
    def wait_for_input(self, timeout_ms=100):
        """Wait for any input with timeout"""
        start_time = time.ticks_ms()
        
        while True:
            current_time = time.ticks_ms()
            
            # Check timeout
            if time.ticks_diff(current_time, start_time) > timeout_ms:
                return None
            
            # Debounce check
            if time.ticks_diff(current_time, self.last_input_time) < self.debounce_ms:
                time.sleep_ms(10)
                continue
            
            # === CHECK JOYSTICK ===
            try:
                direction = self.hw.joystick.get_direction()
                if direction and direction != 'center':
                    self.last_input_time = current_time
                    return direction
                    
                if self.hw.joystick.get_button_press():
                    self.last_input_time = current_time
                    return 'select'
                    
            except Exception as e:
                print(f"Joystick input error: {e}")
            
            # === CHECK PHYSICAL BUTTONS ===
            try:
                self.hw.buttons.update()
                if self.hw.buttons.get_select_press():
                    print("Settings: Button 1 (select) detected")
                    self.last_input_time = current_time
                    return 'select'
                    
                if self.hw.buttons.get_back_press():
                    print("Settings: Button 2 (back) detected")
                    self.last_input_time = current_time
                    return 'exit'
                    
            except Exception as e:
                print(f"Button input error: {e}")
            
            # === CHECK TOUCH SCREEN ===
            # Skip touch if it's having I2C errors
            if hasattr(self.hw, 'touch') and self.hw.touch:
                try:
                    touch_data = self.hw.touch.get_touch()
                    if touch_data:
                        x, y = touch_data[0], touch_data[1]
                        print(f"Touch detected: {x}, {y}")
                        
                        # Simple touch zones
                        if y > 400:  # Bottom navigation area
                            if x < 107:  # Prayer tab
                                self.last_input_time = current_time
                                return 'tab_prayer'
                            elif x < 214:  # Hijri tab
                                self.last_input_time = current_time
                                return 'tab_hijri'
                            # Settings tab is current, ignore
                        else:  # Settings area
                            self.last_input_time = current_time
                            return 'select'
                            
                except OSError as e:
                    if e.errno == 5:  # I2C error
                        # Silently ignore I2C errors
                        pass
                    else:
                        print(f"Touch error: {e}")
                except:
                    # Silently ignore other touch errors
                    pass
            
            time.sleep_ms(20)  # Slightly longer sleep to reduce CPU usage
    
    def draw_simple_menu(self, items, selected):
        """Draw settings menu with scrolling support"""
        try:
            # Clear screen
            self.ui.display.clear(0x0000)  # Black using UI manager's clear method
            
            # Draw title
            self.ui.draw_text_centered("Settings", 20, 2, 0xFFFF)
            
            # Calculate visible items (max 8 items to fit on screen)
            max_visible = 8
            y_start = 60
            item_height = 35
            
            # Calculate scroll offset
            if selected < max_visible:
                start_idx = 0
            else:
                start_idx = selected - max_visible + 1
            
            end_idx = min(start_idx + max_visible, len(items))
            
            # Draw visible menu items
            for display_idx, i in enumerate(range(start_idx, end_idx)):
                y_pos = y_start + display_idx * item_height
                
                if i == selected:
                    # Highlight selected item
                    self.ui.display.fill_rect(10, y_pos - 5, 300, item_height - 5, 0x001F)  # Blue background
                    color = 0xFFFF  # White text
                else:
                    color = 0xC618  # Gray text
                
                # Draw text using UI manager
                self.ui.draw_text_centered(items[i], y_pos + 5, 1, color)
            
            # Draw scroll indicator if needed
            if len(items) > max_visible:
                # Show current position
                pos_text = f"{selected + 1}/{len(items)}"
                self.ui.draw_text_centered(pos_text, 380, 1, 0x7BEF)
            
            # Draw bottom navigation
            self.draw_bottom_nav()
            
        except Exception as e:
            print(f"Menu drawing error: {e}")
    
    def draw_bottom_nav(self):
        """Draw bottom navigation with proper tab names"""
        try:
            nav_y = 420
            nav_height = 60
            tab_width = 106
            
            # Prayer tab (inactive)
            self.ui.display.fill_rect(0, nav_y, tab_width, nav_height, 0x2104)  # Dark gray
            self.ui.draw_text_centered_in_area("Prayer", 0, nav_y + 20, tab_width, 1, 0xC618)
            
            # Hijri tab (inactive)
            self.ui.display.fill_rect(tab_width + 1, nav_y, tab_width, nav_height, 0x2104)  # Dark gray
            self.ui.draw_text_centered_in_area("Events", tab_width + 1, nav_y + 20, tab_width, 1, 0xC618)
            
            # Settings tab (active - highlighted)
            self.ui.display.fill_rect((tab_width * 2) + 2, nav_y, tab_width, nav_height, 0x001F)  # Blue
            self.ui.draw_text_centered_in_area("Settings", (tab_width * 2) + 2, nav_y + 20, tab_width, 1, 0xFFFF)
            
            # Draw navigation hints
            self.ui.draw_text_centered("← → Switch Tabs", nav_y - 20, 1, 0x7BEF)
            
        except Exception as e:
            print(f"Navigation drawing error: {e}")
    
    def sync_time_now(self):
        """Perform immediate time synchronization"""
        print("Attempting time sync...")
        try:
            # Import WiFi time sync
            from lib.wifi_time_sync import WiFiTimeSync
            wifi_sync = WiFiTimeSync(self.config)
            
            # Show sync in progress
            self.ui.display.clear(0x0000)
            self.ui.draw_text_centered("Syncing Time...", 200, 2, 0xFFFF)
            self.ui.draw_text_centered("Please wait", 240, 1, 0x7BEF)
            
            # Attempt sync
            if wifi_sync.auto_sync_time():
                # Success
                self.ui.display.clear(0x0000)
                self.ui.draw_text_centered("Time Sync", 180, 2, 0x07E0)  # Green
                self.ui.draw_text_centered("Successful!", 220, 2, 0x07E0)
                print("Manual time sync successful")
            else:
                # Failed
                self.ui.display.clear(0x0000)
                self.ui.draw_text_centered("Time Sync", 180, 2, 0xF800)  # Red
                self.ui.draw_text_centered("Failed", 220, 2, 0xF800)
                self.ui.draw_text_centered("Check WiFi", 260, 1, 0x7BEF)
                print("Manual time sync failed")
                
        except Exception as e:
            # Error
            self.ui.display.clear(0x0000)
            self.ui.draw_text_centered("Time Sync", 180, 2, 0xF800)  # Red
            self.ui.draw_text_centered("Error", 220, 2, 0xF800)
            self.ui.draw_text_centered(str(e)[:20], 260, 1, 0x7BEF)
            print(f"Time sync error: {e}")
        
        # Wait for user to see result
        import time
        time.sleep(2)
    
    def show_wifi_setup(self):
        """Show WiFi setup interface"""
        print("Opening WiFi setup...")
        
        # Get current WiFi status
        current_ssid = self.config.get('wifi_ssid', 'Not Set')
        wifi_enabled = self.config.get('ntp_enabled', True)
        
        wifi_items = [
            f"SSID: {current_ssid[:15]}",  # Truncate long SSIDs
            "Set Password",
            f"NTP Sync: {'ON' if wifi_enabled else 'OFF'}",
            "Test Connection",
            "Back to Settings"
        ]
        
        selected_wifi = 0
        last_selected = -1
        
        while True:
            # Draw WiFi menu
            if selected_wifi != last_selected:
                try:
                    self.ui.display.clear(0x0000)
                    self.ui.draw_text_centered("WiFi Setup", 20, 2, 0xFFFF)
                    
                    y_start = 80
                    item_height = 40
                    
                    for i, item in enumerate(wifi_items):
                        y_pos = y_start + i * item_height
                        
                        if i == selected_wifi:
                            # Highlight selected
                            self.ui.display.fill_rect(10, y_pos - 5, 300, item_height - 5, 0x001F)
                            color = 0xFFFF
                        else:
                            color = 0xC618
                        
                        self.ui.draw_text_centered(item, y_pos + 5, 1, color)
                    
                    last_selected = selected_wifi
                    
                except Exception as e:
                    print(f"WiFi menu drawing error: {e}")
            
            # Handle WiFi input
            input_result = self.wait_for_input(timeout_ms=100)
            
            if input_result == 'up':
                selected_wifi = (selected_wifi - 1) % len(wifi_items)
            elif input_result == 'down':
                selected_wifi = (selected_wifi + 1) % len(wifi_items)
            elif input_result == 'select':
                if selected_wifi == 0:  # SSID
                    print("SSID setting not implemented - use wifi_config.py")
                elif selected_wifi == 1:  # Password
                    print("Password setting not implemented - use wifi_config.py")
                elif selected_wifi == 2:  # NTP Sync toggle
                    current = self.config.get('ntp_enabled', True)
                    self.config.set('ntp_enabled', not current)
                    wifi_items[2] = f"NTP Sync: {'ON' if not current else 'OFF'}"
                elif selected_wifi == 3:  # Test Connection
                    self.test_wifi_connection()
                elif selected_wifi == 4:  # Back
                    break
            elif input_result == 'exit':
                break
    
    def test_wifi_connection(self):
        """Test WiFi connectivity"""
        print("Testing WiFi connection...")
        
        try:
            self.ui.display.clear(0x0000)
            self.ui.draw_text_centered("Testing WiFi...", 200, 2, 0xFFFF)
            
            # Import network module
            import network
            wlan = network.WLAN(network.STA_IF)
            
            if wlan.isconnected():
                # Connected
                self.ui.display.clear(0x0000)
                self.ui.draw_text_centered("WiFi Connected", 180, 2, 0x07E0)  # Green
                ip = wlan.ifconfig()[0]
                self.ui.draw_text_centered(f"IP: {ip}", 220, 1, 0x7BEF)
                print(f"WiFi connected, IP: {ip}")
            else:
                # Not connected
                self.ui.display.clear(0x0000)
                self.ui.draw_text_centered("WiFi Not", 180, 2, 0xF800)  # Red
                self.ui.draw_text_centered("Connected", 220, 2, 0xF800)
                print("WiFi not connected")
                
        except Exception as e:
            # Error
            self.ui.display.clear(0x0000)
            self.ui.draw_text_centered("WiFi Test", 180, 2, 0xF800)  # Red
            self.ui.draw_text_centered("Error", 220, 2, 0xF800)
            print(f"WiFi test error: {e}")
        
        # Wait for user to see result
        import time
        time.sleep(2)