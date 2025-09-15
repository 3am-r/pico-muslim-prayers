"""
WiFi Time Sync Module for Muslim Companion
Automatically synchronizes device clock using NTP over WiFi
"""

import network
import socket
import struct
import time
from machine import RTC

class WiFiTimeSync:
    def __init__(self, config):
        """Initialize WiFi time sync module"""
        self.config = config
        self.rtc = RTC()
        self.wlan = network.WLAN(network.STA_IF)
        
        # NTP servers (in order of preference)
        self.ntp_servers = [
            "pool.ntp.org",
            "time.nist.gov", 
            "time.google.com",
            "0.pool.ntp.org"
        ]
        
        # NTP packet format constants
        self.NTP_QUERY = bytearray(48)
        self.NTP_QUERY[0] = 0x1B  # NTP version 3, client mode
        
    def connect_wifi(self, ssid=None, password=None, timeout=15):
        """Connect to WiFi network"""
        # Get WiFi credentials from config or parameters
        wifi_ssid = ssid or self.config.get('wifi_ssid')
        wifi_password = password or self.config.get('wifi_password')
        
        if not wifi_ssid:
            print("WiFi: No SSID configured")
            return False
            
        print(f"WiFi: Connecting to {wifi_ssid}...")
        
        # Activate WiFi interface
        self.wlan.active(True)
        
        # Connect to network
        self.wlan.connect(wifi_ssid, wifi_password)
        
        # Wait for connection
        start_time = time.time()
        while not self.wlan.isconnected():
            if time.time() - start_time > timeout:
                print("WiFi: Connection timeout")
                return False
            time.sleep(0.5)
            print(".", end="")
        
        print(f"\nWiFi: Connected! IP: {self.wlan.ifconfig()[0]}")
        return True
        
    def disconnect_wifi(self):
        """Disconnect from WiFi to save power"""
        if self.wlan.isconnected():
            self.wlan.disconnect()
        self.wlan.active(False)
        print("WiFi: Disconnected")
        
    def get_ntp_time(self, server, timeout=5):
        """Get time from NTP server"""
        try:
            # Resolve server address
            addr_info = socket.getaddrinfo(server, 123)
            addr = addr_info[0][-1]
            
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            # Send NTP query
            sock.sendto(self.NTP_QUERY, addr)
            
            # Receive response
            data, _ = sock.recvfrom(48)
            sock.close()
            
            # Extract timestamp from NTP response
            # NTP timestamp is at bytes 40-43 (transmit timestamp)
            timestamp = struct.unpack("!I", data[40:44])[0]
            
            # Convert NTP timestamp to Unix timestamp
            # NTP epoch is Jan 1, 1900; Unix epoch is Jan 1, 1970
            # Difference is 70 years = 2208988800 seconds
            unix_timestamp = timestamp - 2208988800
            
            return unix_timestamp
            
        except Exception as e:
            print(f"NTP: Error getting time from {server}: {e}")
            return None
            
    def sync_time_from_ntp(self):
        """Synchronize RTC with NTP time"""
        print("NTP: Starting time synchronization...")
        
        for server in self.ntp_servers:
            print(f"NTP: Trying {server}...")
            timestamp = self.get_ntp_time(server)
            
            if timestamp:
                # Convert timestamp to datetime tuple
                time_tuple = time.gmtime(timestamp)
                
                # Get timezone offset considering DST
                from lib.dst_utils import get_current_timezone_offset
                base_timezone = self.config.get('timezone', -5)  # Base timezone
                daylight_saving = self.config.get('daylight_saving', True)
                tz_offset = get_current_timezone_offset(base_timezone, daylight_saving)
                
                # Apply timezone offset
                local_timestamp = timestamp + (tz_offset * 3600)
                local_time = time.gmtime(local_timestamp)
                
                # Set RTC (year, month, day, weekday, hour, minute, second, subsecond)
                rtc_tuple = (
                    local_time[0],  # year
                    local_time[1],  # month  
                    local_time[2],  # day
                    local_time[6],  # weekday (0=Monday)
                    local_time[3],  # hour
                    local_time[4],  # minute
                    local_time[5],  # second
                    0               # subsecond
                )
                
                self.rtc.datetime(rtc_tuple)
                
                print(f"NTP: Time synchronized with {server}")
                print(f"NTP: Local time set to: {local_time[0]}-{local_time[1]:02d}-{local_time[2]:02d} {local_time[3]:02d}:{local_time[4]:02d}:{local_time[5]:02d}")
                return True
                
        print("NTP: Failed to synchronize time from any server")
        return False
        
    def auto_sync_time(self, ssid=None, password=None):
        """Complete automatic time sync process"""
        try:
            # Check if already connected
            if not self.wlan.isconnected():
                if not self.connect_wifi(ssid, password):
                    return False
                    
            # Sync time
            success = self.sync_time_from_ntp()
            
            # Disconnect to save power (optional - keep if you want to stay connected)
            if self.config.get('wifi_auto_disconnect', True):
                self.disconnect_wifi()
                
            return success
            
        except Exception as e:
            print(f"WiFi Sync: Error during auto sync: {e}")
            return False
            
    def is_wifi_connected(self):
        """Check if WiFi is connected"""
        return self.wlan.isconnected()
        
    def get_wifi_status(self):
        """Get detailed WiFi status"""
        if self.wlan.isconnected():
            config = self.wlan.ifconfig()
            return {
                'connected': True,
                'ip': config[0],
                'subnet': config[1], 
                'gateway': config[2],
                'dns': config[3],
                'rssi': self.wlan.status('rssi') if hasattr(self.wlan, 'status') else None
            }
        else:
            return {'connected': False}
            
    def configure_wifi_credentials(self, ssid, password):
        """Save WiFi credentials to config"""
        self.config.set('wifi_ssid', ssid)
        self.config.set('wifi_password', password)
        print(f"WiFi: Credentials saved for {ssid}")
        
    def scheduled_sync(self):
        """Perform scheduled time sync (call this periodically)"""
        # Get last sync time
        last_sync = self.config.get('last_ntp_sync', 0)
        current_time = time.time()
        
        # Sync interval in seconds (default: 24 hours)
        sync_interval = self.config.get('ntp_sync_interval', 24 * 3600)
        
        if current_time - last_sync > sync_interval:
            print("NTP: Performing scheduled time sync...")
            if self.auto_sync_time():
                self.config.set('last_ntp_sync', current_time)
                return True
        return False