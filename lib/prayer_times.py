"""
Fixed Prayer Times Calculator for MicroPython
Based on astronomical calculations
"""

import math
from machine import RTC
from lib.dst_utils import get_current_timezone_offset

class PrayerTimes:
    def __init__(self, latitude, longitude, timezone, calculation_method='ISNA', config=None):
        self.latitude = latitude
        self.longitude = longitude
        self.base_timezone = timezone  # Store base timezone
        self.timezone = timezone
        self.calculation_method = calculation_method
        self.config = config
        
        # Method parameters
        self.methods = {
            'ISNA': {
                'fajr': 15,
                'isha': 15
            },
            'MWL': {
                'fajr': 18,
                'isha': 17
            },
            'Mecca': {
                'fajr': 18.5,
                'isha': 90  # 90 minutes after Maghrib
            }
        }
        
        # Madhab for Asr calculation
        self.asr_madhab = 1  # 1 = Shafi (default), 2 = Hanafi
        
        # RTC for time keeping
        self.rtc = RTC()
        
        # Prayer times cache
        self.prayer_times_cache = {}
        self.last_update_day = -1
        
    def calculate_times(self, year, month, day):
        """Calculate prayer times for a given date"""
        # Julian day
        julian_day = self.gregorian_to_julian(year, month, day)
        
        # Calculate solar coordinates
        T = (julian_day - 2451545.0) / 36525  # Julian century
        
        # Solar declination and equation of time
        sun_data = self.sun_position(T)
        decl = sun_data['declination']
        eqt = sun_data['equation']
        
        # Calculate transit (solar noon) - this is the key fix
        # Solar noon in local solar time is 12:00
        # Adjust for equation of time
        transit = 12 - eqt
        
        # Calculate sunrise and sunset
        sunrise_angle = -0.833  # Solar altitude for sunrise/sunset
        sunrise = self.calculate_horizon_time(transit, sunrise_angle, decl, False)
        sunset = self.calculate_horizon_time(transit, sunrise_angle, decl, True)
        
        # Get method parameters
        method = self.methods.get(self.calculation_method, self.methods['ISNA'])
        
        # Calculate Fajr (sun is below horizon, so angle is negative)
        fajr_angle = -method['fajr']  # Make it negative
        fajr = self.calculate_horizon_time(transit, fajr_angle, decl, False)
        
        # Calculate Asr
        # Shadow length factor: 1 for Shafi, 2 for Hanafi
        shadow_factor = self.asr_madhab
        # Calculate the sun altitude angle when shadow = factor * object height
        asr_angle = math.degrees(math.atan(1.0 / (shadow_factor + math.tan(math.radians(abs(self.latitude - decl))))))
        # Calculate hour angle
        cos_h = (math.sin(math.radians(asr_angle)) - 
                math.sin(math.radians(decl)) * math.sin(math.radians(self.latitude))) / \
               (math.cos(math.radians(decl)) * math.cos(math.radians(self.latitude)))
        
        if cos_h > 1:
            cos_h = 1
        elif cos_h < -1:
            cos_h = -1
            
        asr = transit + math.degrees(math.acos(cos_h)) / 15
        
        # Calculate Maghrib (sunset + 3 minutes)
        maghrib = sunset + 3/60
        
        # Calculate Isha
        if method['isha'] > 90:
            # Fixed time after Maghrib
            isha = maghrib + method['isha'] / 60
        else:
            # Angle-based calculation (sun is below horizon, so angle is negative)
            isha_angle = -method['isha']  # Make it negative
            isha = self.calculate_horizon_time(transit, isha_angle, decl, True)
        
        # Prepare times dictionary
        times = {
            'Fajr': self.hours_to_time(fajr, True),
            'Sunrise': self.hours_to_time(sunrise, True),
            'Dhuhr': self.hours_to_time(transit, True),
            'Asr': self.hours_to_time(asr, True),
            'Maghrib': self.hours_to_time(maghrib, True),
            'Isha': self.hours_to_time(isha, True)
        }
        
        return times
    
    def calculate_horizon_time(self, transit, angle, declination, after_transit):
        """Calculate time for a specific sun altitude angle"""
        cos_h = (math.sin(math.radians(angle)) - 
                math.sin(math.radians(declination)) * math.sin(math.radians(self.latitude))) / \
               (math.cos(math.radians(declination)) * math.cos(math.radians(self.latitude)))
        
        if cos_h > 1:
            cos_h = 1
        elif cos_h < -1:
            cos_h = -1
            
        hour_angle = math.degrees(math.acos(cos_h)) / 15
        
        if after_transit:
            return transit + hour_angle
        else:
            return transit - hour_angle
    
    def sun_position(self, T):
        """Calculate sun's declination and equation of time"""
        # Mean solar longitude
        L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
        L0 = L0 % 360
        
        # Mean anomaly
        M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
        M = M % 360
        
        # Equation of center
        C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(math.radians(M)) + \
            (0.019993 - 0.000101 * T) * math.sin(math.radians(2 * M)) + \
            0.000289 * math.sin(math.radians(3 * M))
        
        # True longitude
        L = L0 + C
        
        # Obliquity of ecliptic
        epsilon = 23.439 - 0.00000036 * T
        
        # Declination
        decl = math.degrees(math.asin(math.sin(math.radians(epsilon)) * math.sin(math.radians(L))))
        
        # Right ascension
        RA = math.degrees(math.atan2(math.cos(math.radians(epsilon)) * math.sin(math.radians(L)), 
                                     math.cos(math.radians(L))))
        RA = (RA + 360) % 360
        
        # Equation of time (in hours)
        eqt = (L0 - RA) / 15
        
        # Ensure equation of time is in proper range
        if eqt > 12:
            eqt -= 24
        elif eqt < -12:
            eqt += 24
            
        return {'declination': decl, 'equation': eqt}
    
    def gregorian_to_julian(self, year, month, day):
        """Convert Gregorian date to Julian day"""
        if month <= 2:
            year -= 1
            month += 12
        
        a = math.floor(year / 100)
        b = 2 - a + math.floor(a / 4)
        
        jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5
        return jd
    
    def hours_to_time(self, hours, apply_timezone=False):
        """Convert decimal hours to time string"""
        if apply_timezone:
            # Apply timezone and longitude correction
            # Convert from local solar time to standard time
            # For western longitudes (negative), we need to subtract the longitude correction
            longitude_correction = -self.longitude / 15  # Note the negative sign
            hours = hours + longitude_correction + self.timezone
            
        # Normalize to 24-hour format
        while hours < 0:
            hours += 24
        while hours >= 24:
            hours -= 24
            
        h = int(hours)
        m = int((hours - h) * 60)
        
        # Return in 24-hour format
        return f"{h:02d}:{m:02d}"
    
    def update_prayer_times(self):
        """Calculate prayer times for current day"""
        year, month, day, _, hour, minute, second, _ = self.rtc.datetime()
        
        # Update timezone based on DST settings if config is available
        if self.config:
            daylight_saving_enabled = self.config.get('daylight_saving', True)
            self.timezone = get_current_timezone_offset(self.base_timezone, daylight_saving_enabled)
        
        if day != self.last_update_day:
            print(f"Calculating prayer times for {year}-{month:02d}-{day:02d}")
            print(f"Using timezone: UTC{self.timezone:+d}")
            self.prayer_times_cache = self.calculate_times(year, month, day)
            self.last_update_day = day
        
        return self.prayer_times_cache
            
    def get_next_prayer(self):
        """Determine the next prayer time"""
        if not self.prayer_times_cache:
            self.update_prayer_times()
            
        _, _, _, _, hour, minute, _, _ = self.rtc.datetime()
        current_minutes = hour * 60 + minute
        
        prayer_order = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
        
        for prayer in prayer_order:
            if prayer in self.prayer_times_cache:
                prayer_time = self.prayer_times_cache[prayer]
                prayer_hour, prayer_min = map(int, prayer_time.split(':'))
                prayer_minutes = prayer_hour * 60 + prayer_min
                
                if prayer_minutes > current_minutes:
                    return prayer, prayer_time
        
        # If all prayers passed, next is Fajr tomorrow
        return 'Fajr', self.prayer_times_cache.get('Fajr', '--:--')
    
    def get_prayer_times(self):
        """Get current prayer times (from cache or calculate if needed)"""
        if not self.prayer_times_cache:
            self.update_prayer_times()
        return self.prayer_times_cache
    
    def check_prayer_time_alert(self, hour, minute):
        """Check if current time matches any prayer time"""
        if not self.prayer_times_cache:
            self.update_prayer_times()
        
        current_time = f"{hour:02d}:{minute:02d}"
        
        # Check if current time matches any prayer time
        for prayer_name, prayer_time in self.prayer_times_cache.items():
            if prayer_time == current_time:
                return prayer_name
        
        return None

# Test the fixed implementation
if __name__ == "__main__":
    # Tampa coordinates
    latitude = 27.9506
    longitude = -82.4572
    timezone = -4  # EDT
    
    calc = PrayerTimesFixed(latitude, longitude, timezone, 'ISNA')
    times = calc.calculate_times(2025, 9, 3)
    
    print("Prayer Times for Tampa, FL - September 3, 2025")
    print("=" * 50)
    for prayer, time in times.items():
        print(f"{prayer:8s}: {time}")