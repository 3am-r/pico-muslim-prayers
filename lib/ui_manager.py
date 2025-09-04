"""
UI Manager for Prayer Times Application
Handles display layout and touch interactions
"""

from lib.st7796 import *
from lib.font import Font

class UIManager:
    def __init__(self, display, touch, width, height):
        self.display = display
        self.touch = touch
        self.width = width
        self.height = height
        
        # UI Colors
        self.bg_color = BLACK
        self.primary_color = GREEN
        self.secondary_color = WHITE
        self.accent_color = CYAN
        self.prayer_active_color = YELLOW
        self.prayer_passed_color = GREY
        
        # Font
        self.font = Font()
        
        # Touch regions
        self.touch_regions = []
        
        # Current screen
        self.current_screen = 'main'
        
    def show_splash_screen(self):
        """Display splash screen on startup"""
        self.display.clear(self.bg_color)
        
        # Simple masjid icon using basic characters
        y_pos = 50
        self.draw_text_centered("   ^   ", y_pos, 2, self.primary_color)
        self.draw_text_centered("  / \\  ", y_pos + 16, 2, self.primary_color)
        self.draw_text_centered(" |   | ", y_pos + 32, 2, self.primary_color)
        self.draw_text_centered(" | O | ", y_pos + 48, 2, self.primary_color)
        self.draw_text_centered(" |___| ", y_pos + 64, 2, self.primary_color)
        
        # Title
        self.draw_text_centered("Muslim Companion", y_pos + 100, 3, self.primary_color)
        
        # Shorter messages that fit the 320px width
        self.draw_text_centered("For Yassin's reminder", y_pos + 140, 1, self.secondary_color)
        self.draw_text_centered("And remembrance of Allah", y_pos + 160, 1, self.secondary_color)
        self.draw_text_centered("is greater", y_pos + 180, 1, self.secondary_color)
        
        # Loading bar (static, no animation)
        bar_width = 200
        bar_height = 10
        bar_x = (self.width - bar_width) // 2
        bar_y = self.height * 2 // 3
        
        self.display.draw_rect(bar_x, bar_y, bar_width, bar_height, self.secondary_color)
        self.display.fill_rect(bar_x + 1, bar_y + 1, bar_width - 2, bar_height - 2, self.primary_color)
            
    def draw_main_screen(self, current_time, prayer_times, next_prayer, next_time, location, current_tab='prayer'):
        """Draw main prayer times screen"""
        self.display.clear(self.bg_color)
        self.touch_regions = []
        
        # Header with current time and location
        self.draw_header(current_time, location)
        
        # Next prayer highlight
        self.draw_next_prayer(next_prayer, next_time, current_time)
        
        # All prayer times grid
        self.draw_prayer_times_grid(prayer_times, next_prayer)
        
        # Navigation instructions (positioned above bottom navigation)
        self.draw_text_centered("Left/Right: Tabs  Button1: Settings  Button2: Refresh", 
                               self.height - 90, 1, GREY)
        
        # Bottom navigation
        self.draw_bottom_navigation(current_tab)
        
    def draw_header(self, current_time, location):
        """Draw header with time and location"""
        # Background for header
        self.display.fill_rect(0, 0, self.width, 60, self.primary_color)
        
        # Current time (adjust size for 12h format)
        if 'AM' in current_time or 'PM' in current_time:
            # Use smaller size for 12h format to fit
            self.draw_text_centered(current_time, 20, 2, BLACK)
        else:
            self.draw_text_centered(current_time, 20, 3, BLACK)
        
        # Location
        self.draw_text_centered(location, 45, 1, BLACK)
    
    def update_time_display(self, current_time):
        """Update only the time display in the header"""
        # Clear the time area only (wider for AM/PM format)
        time_area_width = min(250, len(current_time) * 6 * 3 + 30)  # Text width + padding, max 250px
        time_x = (self.width - time_area_width) // 2
        self.display.fill_rect(time_x, 15, time_area_width, 25, self.primary_color)
        
        # Redraw the time (adjust size if needed for AM/PM)
        if 'AM' in current_time or 'PM' in current_time:
            # Use smaller size for 12h format to fit
            self.draw_text_centered(current_time, 20, 2, BLACK)
        else:
            self.draw_text_centered(current_time, 20, 3, BLACK)
        
    def draw_next_prayer(self, next_prayer, next_time, current_time):
        """Draw next prayer highlight section"""
        y_pos = 70
        
        # Background
        self.display.fill_rect(10, y_pos, self.width - 20, 80, DARK_GREEN)
        self.display.draw_rect(10, y_pos, self.width - 20, 80, self.primary_color)
        
        # Next prayer label
        self.draw_text_centered("Next Prayer", y_pos + 10, 1, self.secondary_color)
        
        # Prayer name and time
        if next_prayer and next_time:
            self.draw_text_centered(next_prayer, y_pos + 35, 3, self.accent_color)
            self.draw_text_centered(next_time, y_pos + 60, 2, WHITE)
            
            # Calculate and show time remaining
            time_remaining = self.calculate_time_remaining(current_time, next_time)
            if time_remaining:
                self.draw_text_centered(f"in {time_remaining}", y_pos + 65, 1, GREY)
    
    def draw_prayer_times_grid(self, prayer_times, next_prayer):
        """Draw all prayer times in a grid"""
        prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
        
        # Grid layout: 2 columns, 3 rows (adjusted for bottom navigation)
        grid_y = 170
        grid_height = 180  # Reduced height for bottom navigation
        cell_width = self.width // 2 - 15
        cell_height = grid_height // 3
        
        for i, prayer in enumerate(prayers):
            col = i % 2
            row = i // 2
            
            x = 10 + col * (cell_width + 10)
            y = grid_y + row * (cell_height + 5)
            
            # Determine color based on prayer status
            if prayer == next_prayer:
                bg_color = self.prayer_active_color
                text_color = BLACK
            else:
                bg_color = BLACK
                text_color = self.secondary_color
                
            # Draw prayer cell
            self.display.fill_rect(x, y, cell_width, cell_height - 5, bg_color)
            self.display.draw_rect(x, y, cell_width, cell_height - 5, self.primary_color)
            
            # Prayer name
            self.draw_text(prayer, x + 10, y + 10, 2, text_color)
            
            # Prayer time (smaller size if AM/PM format)
            time_str = prayer_times.get(prayer, '--:--')
            if 'AM' in time_str or 'PM' in time_str:
                self.draw_text(time_str, x + 10, y + 40, 1, WHITE if bg_color == BLACK else BLACK)
            else:
                self.draw_text(time_str, x + 10, y + 40, 2, WHITE if bg_color == BLACK else BLACK)
            
    def draw_bottom_navigation(self, current_tab):
        """Draw bottom navigation bar with tabs"""
        nav_height = 60
        nav_y = self.height - nav_height
        
        # Background for navigation
        self.display.fill_rect(0, nav_y, self.width, nav_height, 0x2104)  # Dark gray
        
        # Tab width
        tab_width = self.width // 3
        
        # Prayer Times Tab
        prayer_active = current_tab == 'prayer'
        self.draw_nav_tab(0, nav_y, tab_width, nav_height, "Prayer", prayer_active, "🕌", 'prayer')
        
        # Hijri Events Tab  
        hijri_active = current_tab == 'hijri'
        self.draw_nav_tab(tab_width, nav_y, tab_width, nav_height, "Events", hijri_active, "📅", 'hijri')
        
        # Settings Tab
        settings_active = current_tab == 'settings'
        self.draw_nav_tab(tab_width * 2, nav_y, tab_width, nav_height, "Settings", settings_active, "⚙️", 'settings')
    
    def draw_nav_tab(self, x, y, width, height, label, active, icon, tab_id):
        """Draw a single navigation tab"""
        # Tab background
        if active:
            self.display.fill_rect(x, y, width, height, self.primary_color)
            text_color = BLACK
        else:
            text_color = self.secondary_color
        
        # Tab border
        self.display.draw_rect(x, y, width, height, self.secondary_color)
        
        # Icon (using ASCII art)
        icon_y = y + 8
        if icon == "🕌":  # Mosque for Prayer
            self.draw_text_centered_in_area("_^_", x, icon_y, width, 1, text_color)
            self.draw_text_centered_in_area("|O|", x, icon_y + 8, width, 1, text_color)
            self.draw_text_centered_in_area("|_|", x, icon_y + 16, width, 1, text_color)
        elif icon == "📅":  # Calendar for Events
            self.draw_text_centered_in_area("===", x, icon_y, width, 1, text_color)
            self.draw_text_centered_in_area("|1|", x, icon_y + 8, width, 1, text_color)
            self.draw_text_centered_in_area("---", x, icon_y + 16, width, 1, text_color)
        elif icon == "⚙️":  # Gear for Settings
            self.draw_text_centered_in_area("+-+", x, icon_y, width, 1, text_color)
            self.draw_text_centered_in_area("|O|", x, icon_y + 8, width, 1, text_color)
            self.draw_text_centered_in_area("+-+", x, icon_y + 16, width, 1, text_color)
        
        # Label (positioned below the 3-line icon)
        label_y = y + height - 15
        self.draw_text_centered_in_area(label, x, label_y, width, 1, text_color)
        
        # Add touch region
        self.touch_regions.append({
            'x': x,
            'y': y,
            'w': width,
            'h': height,
            'action': f'tab_{tab_id}'
        })
    
    def draw_text_centered_in_area(self, text, x, y, width, size, color):
        """Draw text centered within a specific area"""
        text_width = len(text) * 6 * size
        text_x = x + (width - text_width) // 2
        self.font.draw_text(self.display, text, text_x, y, size, color)
    
    def draw_hijri_screen(self, hijri_date, next_event, days_until, current_tab='hijri'):
        """Draw Hijri events screen"""
        self.display.clear(self.bg_color)
        self.touch_regions = []
        
        # Header
        self.display.fill_rect(0, 0, self.width, 60, self.primary_color)
        self.draw_text_centered("Islamic Calendar", 20, 2, BLACK)
        
        # Current Hijri date
        y_pos = 80
        self.draw_text_centered("Today's Date", y_pos, 2, self.primary_color)
        self.draw_text_centered(hijri_date, y_pos + 30, 2, self.secondary_color)
        
        # Next Islamic event
        y_pos += 80
        self.display.fill_rect(10, y_pos, self.width - 20, 100, DARK_GREEN)
        self.display.draw_rect(10, y_pos, self.width - 20, 100, self.primary_color)
        
        self.draw_text_centered("Next Event", y_pos + 15, 1, self.secondary_color)
        self.draw_text_centered(next_event, y_pos + 40, 2, self.accent_color)
        
        if days_until > 0:
            days_text = f"in {days_until} days"
        elif days_until == 0:
            days_text = "Today!"
        else:
            days_text = "Soon"
        
        self.draw_text_centered(days_text, y_pos + 70, 1, WHITE)
        
        # Islamic months info
        y_pos += 120
        self.draw_text_centered("Current Islamic Year", y_pos, 1, self.secondary_color)
        hijri_year = hijri_date.split()[-1]  # Extract year from date string
        self.draw_text_centered(f"{hijri_year} AH", y_pos + 20, 2, self.primary_color)
        
        # Navigation instructions (positioned above bottom navigation)
        self.draw_text_centered("Left/Right: Switch Tabs  Button1: Settings", 
                               self.height - 90, 1, GREY)
        
        # Bottom navigation
        self.draw_bottom_navigation(current_tab)
        
    def show_settings_screen(self, config):
        """Display settings screen with city selection"""
        self.display.clear(self.bg_color)
        self.touch_regions = []
        self.current_screen = 'settings'
        
        # Header
        self.display.fill_rect(0, 0, self.width, 50, self.primary_color)
        self.draw_text_centered("Settings", 20, 2, BLACK)
        
        # Back button
        self.display.fill_rect(10, 10, 60, 30, RED)
        self.draw_text("Back", 20, 18, 1, WHITE)
        self.touch_regions.append({
            'x': 10, 'y': 10, 'w': 60, 'h': 30,
            'action': 'back'
        })
        
        # City selection menu
        self.draw_city_menu(config)
        
        # Calculation method selection
        self.draw_method_menu(config)
        
    def draw_city_menu(self, config):
        """Draw US cities selection menu"""
        cities = [
            {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060, 'tz': -5},
            {'name': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437, 'tz': -8},
            {'name': 'Chicago', 'lat': 41.8781, 'lon': -87.6298, 'tz': -6},
            {'name': 'Houston', 'lat': 29.7604, 'lon': -95.3698, 'tz': -6},
            {'name': 'Phoenix', 'lat': 33.4484, 'lon': -112.0740, 'tz': -7},
            {'name': 'Philadelphia', 'lat': 39.9526, 'lon': -75.1652, 'tz': -5},
            {'name': 'San Antonio', 'lat': 29.4241, 'lon': -98.4936, 'tz': -6},
            {'name': 'San Diego', 'lat': 32.7157, 'lon': -117.1611, 'tz': -8},
            {'name': 'Dallas', 'lat': 32.7767, 'lon': -96.7970, 'tz': -6},
            {'name': 'Detroit', 'lat': 42.3314, 'lon': -83.0458, 'tz': -5},
            {'name': 'Miami', 'lat': 25.7617, 'lon': -80.1918, 'tz': -5},
            {'name': 'Boston', 'lat': 42.3601, 'lon': -71.0589, 'tz': -5}
        ]
        
        y_pos = 70
        self.draw_text("Select City:", 10, y_pos, 2, self.secondary_color)
        y_pos += 30
        
        # Display cities in scrollable list (show first 6)
        for i, city in enumerate(cities[:6]):
            btn_y = y_pos + i * 35
            
            # Highlight selected city
            current_city = config.get('location_name', 'New York')
            if city['name'] == current_city:
                bg_color = self.primary_color
                text_color = BLACK
            else:
                bg_color = BLACK
                text_color = self.secondary_color
                
            self.display.fill_rect(10, btn_y, self.width - 20, 30, bg_color)
            self.display.draw_rect(10, btn_y, self.width - 20, 30, self.primary_color)
            self.draw_text(city['name'], 20, btn_y + 8, 1, text_color)
            
            # Add touch region
            self.touch_regions.append({
                'x': 10, 'y': btn_y, 'w': self.width - 20, 'h': 30,
                'action': 'select_city',
                'data': city
            })
            
    def draw_method_menu(self, config):
        """Draw calculation method selection"""
        methods = ['ISNA', 'MWL', 'Egypt', 'Mecca', 'Karachi']
        
        y_pos = 300
        self.draw_text("Calculation Method:", 10, y_pos, 1, self.secondary_color)
        y_pos += 25
        
        # Display methods horizontally
        x_pos = 10
        for method in methods:
            current_method = config.get('method', 'ISNA')
            
            if method == current_method:
                bg_color = self.primary_color
                text_color = BLACK
            else:
                bg_color = BLACK
                text_color = self.secondary_color
                
            btn_width = 55
            self.display.fill_rect(x_pos, y_pos, btn_width, 25, bg_color)
            self.display.draw_rect(x_pos, y_pos, btn_width, 25, self.primary_color)
            
            # Center text in button
            text_x = x_pos + (btn_width - len(method) * 6) // 2
            self.draw_text(method, text_x, y_pos + 7, 1, text_color)
            
            # Add touch region
            self.touch_regions.append({
                'x': x_pos, 'y': y_pos, 'w': btn_width, 'h': 25,
                'action': 'select_method',
                'data': method
            })
            
            x_pos += btn_width + 5
            
    def handle_touch(self, x, y):
        """Process touch input and return action"""
        for region in self.touch_regions:
            if (region['x'] <= x <= region['x'] + region['w'] and
                region['y'] <= y <= region['y'] + region['h']):
                return region
        return None
        
    def calculate_time_remaining(self, current_time, next_time):
        """Calculate time remaining until next prayer"""
        try:
            curr_parts = current_time.split(':')
            next_parts = next_time.split(':')
            
            if len(curr_parts) >= 2 and len(next_parts) >= 2:
                curr_minutes = int(curr_parts[0]) * 60 + int(curr_parts[1])
                next_minutes = int(next_parts[0]) * 60 + int(next_parts[1])
                
                diff = next_minutes - curr_minutes
                if diff < 0:
                    diff += 24 * 60  # Next day
                    
                hours = diff // 60
                minutes = diff % 60
                
                if hours > 0:
                    return f"{hours}h {minutes}m"
                else:
                    return f"{minutes}m"
        except:
            pass
        return ""
        
    def draw_text(self, text, x, y, size=1, color=WHITE):
        """Draw text at position"""
        self.font.draw_text(self.display, text, x, y, size, color)
            
    def draw_text_centered(self, text, y, size=1, color=WHITE):
        """Draw centered text"""
        text_width = self.font.get_text_width(text, size)
        x = (self.width - text_width) // 2
        self.font.draw_text(self.display, text, x, y, size, color)
        
    def draw_char(self, char, x, y, size, color):
        """Draw a single character"""
        self.font.draw_char(self.display, char, x, y, size, color)
    
    def draw_settings_menu(self, settings_items, selected_index, config):
        """Draw navigable settings menu"""
        self.display.clear(self.bg_color)
        
        # Header
        self.draw_text_centered("Settings", 20, 2, self.primary_color)
        
        # Menu items (adjusted for bottom navigation)
        y_start = 60
        item_height = 30  # Reduced height to fit more items
        max_items = 6     # Limit items shown at once
        
        for i, item in enumerate(settings_items[:max_items]):
            y_pos = y_start + (i * item_height)
            
            # Highlight selected item
            if i == selected_index:
                self.display.fill_rect(5, y_pos - 3, self.width - 10, item_height - 3, self.primary_color)
                text_color = BLACK
            else:
                text_color = self.secondary_color
            
            # Item name
            self.draw_text(item['name'], 15, y_pos, 1, text_color)
            
            # Current value
            if item['key'] != 'exit':
                current_value = config.get(item['key'], 'N/A')
                value_text = str(current_value)
                if len(value_text) > 12:
                    value_text = value_text[:10] + "..."
                self.draw_text(value_text, 180, y_pos, 1, text_color)
        
        # Instructions (moved higher to avoid navigation)
        self.draw_text_centered("Navigate: Joystick/Buttons", 
                               self.height - 100, 1, GREY)
        
        # Bottom navigation
        self.draw_bottom_navigation('settings')
    
    def draw_number_editor(self, setting_name, current_value):
        """Draw number editor interface"""
        self.display.clear(self.bg_color)
        
        # Header
        self.draw_text_centered(f"Edit {setting_name}", 50, 2, self.primary_color)
        
        # Current value (large)
        value_str = str(current_value)
        self.draw_text_centered(value_str, 150, 4, self.accent_color)
        
        # Instructions (moved higher for bottom navigation)
        self.draw_text_centered("Up/Down: Change Value", 220, 1, self.secondary_color)
        self.draw_text_centered("Right: Save  Left: Cancel", 250, 1, self.secondary_color)
        
        # Bottom navigation
        self.draw_bottom_navigation('settings')