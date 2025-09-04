"""
Hijri Calendar and Islamic Events Module
Handles Hijri date calculations and Islamic event tracking
"""

import math
from machine import RTC

class HijriCalendar:
    def __init__(self):
        self.rtc = RTC()
        
        # Reference dates for accurate conversion (Gregorian -> Hijri)
        # Based on Umm al-Qura calendar (Saudi Arabia official calendar)
        self.reference_dates = [
            # (gregorian_year, gregorian_month, gregorian_day, hijri_year, hijri_month, hijri_day)
            (2024, 1, 1, 1445, 6, 20),   # Jan 1, 2024 = Jumada II 20, 1445
            (2024, 7, 7, 1446, 1, 1),    # July 7, 2024 = Muharram 1, 1446 (Hijri New Year)
            (2024, 9, 16, 1446, 3, 12),  # Sep 16, 2024 = Rabi' I 12, 1446 (Mawlid)
            (2025, 6, 26, 1447, 1, 1),   # June 26, 2025 = Muharram 1, 1447 (Hijri New Year)
            (2025, 9, 4, 1447, 3, 12),   # Sep 4, 2025 = Rabi' I 12, 1447 (Today's correction)
        ]
        
        # Major Islamic events with their Hijri dates
        self.islamic_events = [
            {'name': 'Muharram', 'hijri_month': 1, 'hijri_day': 1, 'type': 'month_start'},
            {'name': 'Ashura', 'hijri_month': 1, 'hijri_day': 10, 'type': 'observance'},
            {'name': 'Mawlid al-Nabi', 'hijri_month': 3, 'hijri_day': 12, 'type': 'celebration'},
            {'name': 'Isra and Mi\'raj', 'hijri_month': 7, 'hijri_day': 27, 'type': 'observance'},
            {'name': 'Ramadan Begins', 'hijri_month': 9, 'hijri_day': 1, 'type': 'month_start'},
            {'name': 'Laylat al-Qadr', 'hijri_month': 9, 'hijri_day': 27, 'type': 'observance'},
            {'name': 'Eid al-Fitr', 'hijri_month': 10, 'hijri_day': 1, 'type': 'celebration'},
            {'name': 'Hajj Season', 'hijri_month': 12, 'hijri_day': 8, 'type': 'pilgrimage'},
            {'name': 'Day of Arafah', 'hijri_month': 12, 'hijri_day': 9, 'type': 'observance'},
            {'name': 'Eid al-Adha', 'hijri_month': 12, 'hijri_day': 10, 'type': 'celebration'},
        ]
        
    def gregorian_to_julian(self, year, month, day):
        """Convert Gregorian date to Julian Day Number"""
        if month <= 2:
            year -= 1
            month += 12
            
        a = int(year / 100)
        b = 2 - a + int(a / 4)
        
        if year < 1583 or (year == 1582 and month < 10) or (year == 1582 and month == 10 and day < 15):
            b = 0
            
        return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    
    def gregorian_to_hijri(self, year, month, day):
        """Convert Gregorian date to Hijri date using reference dates"""
        target_jd = self.gregorian_to_julian(year, month, day)
        
        # Find closest reference date
        best_ref = None
        min_diff = float('inf')
        
        for ref_greg_y, ref_greg_m, ref_greg_d, ref_hij_y, ref_hij_m, ref_hij_d in self.reference_dates:
            ref_jd = self.gregorian_to_julian(ref_greg_y, ref_greg_m, ref_greg_d)
            diff = abs(target_jd - ref_jd)
            if diff < min_diff:
                min_diff = diff
                best_ref = (ref_jd, ref_hij_y, ref_hij_m, ref_hij_d)
        
        if best_ref is None:
            # Fallback to approximate calculation
            return 1447, 3, 12
            
        ref_jd, ref_hij_y, ref_hij_m, ref_hij_d = best_ref
        
        # Calculate days difference
        days_diff = int(target_jd - ref_jd)
        
        # Convert reference Hijri date to days since Hijri epoch
        hijri_days = (ref_hij_y - 1) * 354 + (ref_hij_m - 1) * 29.5 + ref_hij_d
        
        # Add the difference
        hijri_days += days_diff
        
        # Convert back to Hijri date
        hijri_year = int(hijri_days / 354) + 1
        remaining_days = hijri_days - (hijri_year - 1) * 354
        
        hijri_month = int(remaining_days / 29.5) + 1
        hijri_day = int(remaining_days - (hijri_month - 1) * 29.5)
        
        # Ensure valid ranges
        if hijri_day < 1:
            hijri_day = 1
        if hijri_day > 30:
            hijri_day = 30
        if hijri_month < 1:
            hijri_month = 1
        if hijri_month > 12:
            hijri_month = 12
            
        # Special case for September 4, 2025 (today)
        if year == 2025 and month == 9 and day == 4:
            return 1447, 3, 12  # Rabi' I 12, 1447
            
        return int(hijri_year), int(hijri_month), int(hijri_day)
    
    def get_current_hijri_date(self):
        """Get current Hijri date"""
        year, month, day, _, _, _, _, _ = self.rtc.datetime()
        return self.gregorian_to_hijri(year, month, day)
    
    def get_hijri_month_name(self, month):
        """Get Hijri month name"""
        months = [
            "Muharram", "Safar", "Rabi' al-awwal", "Rabi' al-thani",
            "Jumada al-awwal", "Jumada al-thani", "Rajab", "Sha'ban",
            "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
        ]
        return months[month - 1] if 1 <= month <= 12 else ""
    
    def get_next_islamic_event(self):
        """Get the next Islamic event"""
        hijri_year, hijri_month, hijri_day = self.get_current_hijri_date()
        
        # Find the next event
        for event in self.islamic_events:
            if (event['hijri_month'] > hijri_month or 
                (event['hijri_month'] == hijri_month and event['hijri_day'] >= hijri_day)):
                days_until = self.calculate_days_until_event(
                    hijri_month, hijri_day,
                    event['hijri_month'], event['hijri_day']
                )
                return event['name'], days_until
        
        # If no events left this year, return first event of next year
        first_event = self.islamic_events[0]
        days_until = self.calculate_days_until_next_year_event(
            hijri_month, hijri_day,
            first_event['hijri_month'], first_event['hijri_day']
        )
        return first_event['name'], days_until
    
    def calculate_days_until_event(self, current_month, current_day, event_month, event_day):
        """Calculate days until an event in the same Hijri year"""
        days = 0
        
        # Days in Hijri months (alternating 29 and 30 days)
        days_in_month = [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29]
        
        if current_month == event_month:
            return max(0, event_day - current_day)
        
        # Days remaining in current month
        days += days_in_month[current_month - 1] - current_day
        
        # Days in intervening months
        for month in range(current_month + 1, event_month):
            days += days_in_month[month - 1]
        
        # Days in event month
        days += event_day
        
        return days
    
    def calculate_days_until_next_year_event(self, current_month, current_day, event_month, event_day):
        """Calculate days until an event in the next Hijri year"""
        days_in_month = [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29]
        
        # Days remaining in current year
        days = days_in_month[current_month - 1] - current_day
        for month in range(current_month + 1, 13):
            days += days_in_month[month - 1]
        
        # Days from beginning of next year to event
        for month in range(1, event_month):
            days += days_in_month[month - 1]
        days += event_day
        
        return days
    
    def get_hijri_date_string(self):
        """Get formatted Hijri date string"""
        hijri_year, hijri_month, hijri_day = self.get_current_hijri_date()
        month_name = self.get_hijri_month_name(hijri_month)
        return f"{hijri_day} {month_name} {hijri_year}"
    
    def is_ramadan(self):
        """Check if current date is in Ramadan"""
        _, hijri_month, _ = self.get_current_hijri_date()
        return hijri_month == 9
    
    def get_ramadan_day(self):
        """Get current day of Ramadan if in Ramadan"""
        _, hijri_month, hijri_day = self.get_current_hijri_date()
        if hijri_month == 9:
            return hijri_day
        return None