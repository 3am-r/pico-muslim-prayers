"""
WiFi Configuration Example for Muslim Companion
Copy this file to wifi_config.py and update with your WiFi credentials

This is a simple way to configure WiFi without needing a complex input interface
"""

# WiFi Network Credentials
WIFI_SSID = "77"
WIFI_PASSWORD = "77"

# Optional: Set these in your config.json or configure via settings
def configure_wifi(config):
    """Configure WiFi settings in the config object"""
    config.set('wifi_ssid', WIFI_SSID)
    config.set('wifi_password', WIFI_PASSWORD)
    config.set('ntp_enabled', True)
    config.set('ntp_on_startup', True)
    config.set('wifi_auto_connect', True)
    config.set('wifi_auto_disconnect', True)  # Save power after sync
    
    print(f"WiFi configured for network: {WIFI_SSID}")

# To use this configuration:
# 1. Copy this file to wifi_config.py
# 2. Update WIFI_SSID and WIFI_PASSWORD with your credentials  
# 3. Import and call configure_wifi(config) in your main.py initialization
#
# Example in main.py:
# try:
#     from wifi_config import configure_wifi
#     configure_wifi(self.config)
# except ImportError:
#     print("wifi_config.py not found - WiFi features disabled")