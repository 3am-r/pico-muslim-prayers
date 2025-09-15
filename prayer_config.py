"""
Configuration Manager for Prayer Times Application
Handles saving and loading settings
"""

import json

class Config:
    def __init__(self, filename='config.json'):
        self.filename = filename
        self.settings = self.load_default_settings()
        self.load_settings()
        
    def load_default_settings(self):
        """Load default configuration"""
        return {
            'location_name': 'Tampa',
            'latitude': 27.9506,
            'longitude': -82.4572,
            'timezone': -5,  # EST base timezone (without DST)
            'daylight_saving': True,  # Enable daylight saving time adjustment
            'method': 'ISNA',
            'asr_madhab': 1,  # 1 = Shafi, 2 = Hanafi
            'buzzer_enabled': True,
            'buzzer_duration': 5,  # seconds
            'alert_minutes_before': 0,  # Alert exactly at prayer time
            'volume': 5,  # 1-10
            'display_brightness': 8,  # 1-10
            'auto_dst': True,  # Automatic daylight saving time
            'language': 'en',
            'date_format': 'MM/DD/YYYY',
            'time_format': '12h',  # 12h or 24h
            'selected_city': 'Tampa',
            # WiFi and NTP settings
            'wifi_ssid': '',  # WiFi network name
            'wifi_password': '',  # WiFi password
            'wifi_auto_connect': True,  # Auto connect to WiFi on startup
            'wifi_auto_disconnect': True,  # Disconnect after sync to save power
            'ntp_enabled': True,  # Enable automatic time sync
            'ntp_sync_interval': 86400,  # Sync every 24 hours (seconds)
            'last_ntp_sync': 0,  # Last successful NTP sync timestamp
            'ntp_on_startup': True  # Sync time on device startup
        }
        
    def load_settings(self):
        """Load settings from file"""
        try:
            with open(self.filename, 'r') as f:
                saved_settings = json.load(f)
                self.settings.update(saved_settings)
        except:
            # File doesn't exist or is corrupted, use defaults
            self.save_settings()
            
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
        
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()
        
    def update_location(self, city_data):
        """Update location from city selection"""
        self.settings['location_name'] = city_data['name']
        self.settings['latitude'] = city_data['lat']
        self.settings['longitude'] = city_data['lon']
        self.settings['timezone'] = city_data['tz']
        self.settings['selected_city'] = city_data['name']
        self.save_settings()
        
    def get_us_cities(self):
        """Get list of US cities with coordinates and timezones"""
        return [
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
            {'name': 'Boston', 'lat': 42.3601, 'lon': -71.0589, 'tz': -5},
            {'name': 'Seattle', 'lat': 47.6062, 'lon': -122.3321, 'tz': -8},
            {'name': 'Denver', 'lat': 39.7392, 'lon': -104.9903, 'tz': -7},
            {'name': 'Washington DC', 'lat': 38.9072, 'lon': -77.0369, 'tz': -5},
            {'name': 'Atlanta', 'lat': 33.7490, 'lon': -84.3880, 'tz': -5},
            {'name': 'Las Vegas', 'lat': 36.1699, 'lon': -115.1398, 'tz': -8},
            {'name': 'San Francisco', 'lat': 37.7749, 'lon': -122.4194, 'tz': -8},
            {'name': 'Portland', 'lat': 45.5152, 'lon': -122.6784, 'tz': -8},
            {'name': 'Minneapolis', 'lat': 44.9778, 'lon': -93.2650, 'tz': -6},
            {'name': 'Salt Lake City', 'lat': 40.7608, 'lon': -111.8910, 'tz': -7},
            {'name': 'Kansas City', 'lat': 39.0997, 'lon': -94.5786, 'tz': -6},
            {'name': 'St. Louis', 'lat': 38.6270, 'lon': -90.1994, 'tz': -6},
            {'name': 'Orlando', 'lat': 28.5383, 'lon': -81.3792, 'tz': -5},
            {'name': 'Tampa', 'lat': 27.9506, 'lon': -82.4572, 'tz': -5}
        ]
        
    def get_calculation_methods(self):
        """Get available calculation methods"""
        return [
            {'code': 'MWL', 'name': 'Muslim World League'},
            {'code': 'ISNA', 'name': 'Islamic Society of North America'},
            {'code': 'Egypt', 'name': 'Egyptian General Authority'},
            {'code': 'Mecca', 'name': 'Umm Al-Qura, Mecca'},
            {'code': 'Karachi', 'name': 'University of Karachi'},
            {'code': 'Tehran', 'name': 'Institute of Tehran'},
            {'code': 'Jafari', 'name': 'Shia Ithna-Ashari'}
        ]