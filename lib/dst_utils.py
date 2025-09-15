"""
Daylight Saving Time Utilities for Muslim Companion
Handles DST calculations for US locations
"""

import time

def is_dst_active(year, month, day):
    """
    Check if Daylight Saving Time is active for a given date in the US
    
    US DST Rules:
    - Starts: Second Sunday in March at 2:00 AM
    - Ends: First Sunday in November at 2:00 AM
    
    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
        day: Day (1-31)
        
    Returns:
        bool: True if DST is active, False otherwise
    """
    
    # DST doesn't apply to these months
    if month < 3 or month > 11:
        return False
    if month > 3 and month < 11:
        return True
        
    # Calculate DST start and end dates for the year
    dst_start = get_second_sunday_march(year)
    dst_end = get_first_sunday_november(year)
    
    if month == 3:
        return day >= dst_start
    elif month == 11:
        return day < dst_end
    else:
        return True

def get_second_sunday_march(year):
    """Get the day of the second Sunday in March"""
    # March 1st
    march_1_weekday = get_weekday(year, 3, 1)
    
    # Days until first Sunday (0=Sunday, 1=Monday, etc.)
    days_to_first_sunday = (7 - march_1_weekday) % 7
    if days_to_first_sunday == 0 and march_1_weekday == 0:
        days_to_first_sunday = 0  # March 1st is already Sunday
    
    first_sunday = 1 + days_to_first_sunday
    second_sunday = first_sunday + 7
    
    return second_sunday

def get_first_sunday_november(year):
    """Get the day of the first Sunday in November"""
    # November 1st
    nov_1_weekday = get_weekday(year, 11, 1)
    
    # Days until first Sunday
    days_to_first_sunday = (7 - nov_1_weekday) % 7
    if days_to_first_sunday == 0 and nov_1_weekday == 0:
        days_to_first_sunday = 0  # November 1st is already Sunday
        
    first_sunday = 1 + days_to_first_sunday
    
    return first_sunday

def get_weekday(year, month, day):
    """
    Get weekday for a given date using Zeller's congruence
    Returns: 0=Sunday, 1=Monday, 2=Tuesday, ..., 6=Saturday
    """
    if month < 3:
        month += 12
        year -= 1
    
    # Zeller's congruence formula
    q = day
    m = month
    k = year % 100
    j = year // 100
    
    h = (q + ((13 * (m + 1)) // 5) + k + (k // 4) + (j // 4) - 2 * j) % 7
    
    # Convert to our format (0=Sunday)
    weekday = (h + 5) % 7
    return weekday

def get_current_timezone_offset(base_timezone, daylight_saving_enabled=True):
    """
    Get the current timezone offset accounting for DST
    
    Args:
        base_timezone: Base timezone offset (e.g., -5 for EST)
        daylight_saving_enabled: Whether DST is enabled in settings
        
    Returns:
        int: Current timezone offset
    """
    if not daylight_saving_enabled:
        return base_timezone
        
    # Get current date
    current_time = time.localtime()
    year = current_time[0]
    month = current_time[1] 
    day = current_time[2]
    
    # Check if DST is currently active
    if is_dst_active(year, month, day):
        return base_timezone + 1  # Add 1 hour for DST
    else:
        return base_timezone

def format_timezone_display(base_timezone, daylight_saving_enabled=True):
    """
    Format timezone for display in settings
    
    Args:
        base_timezone: Base timezone offset
        daylight_saving_enabled: Whether DST is enabled
        
    Returns:
        str: Formatted timezone string
    """
    current_offset = get_current_timezone_offset(base_timezone, daylight_saving_enabled)
    
    if daylight_saving_enabled:
        current_time = time.localtime()
        if is_dst_active(current_time[0], current_time[1], current_time[2]):
            dst_status = " (DST)"
        else:
            dst_status = " (STD)"
    else:
        dst_status = ""
        
    if current_offset >= 0:
        return f"UTC+{current_offset}{dst_status}"
    else:
        return f"UTC{current_offset}{dst_status}"

# Example timezone mappings for US cities
US_TIMEZONES = {
    'Eastern': -5,    # EST (becomes -4 EDT in summer)
    'Central': -6,    # CST (becomes -5 CDT in summer) 
    'Mountain': -7,   # MST (becomes -6 MDT in summer)
    'Pacific': -8,    # PST (becomes -7 PDT in summer)
    'Alaska': -9,     # AKST (becomes -8 AKDT in summer)
    'Hawaii': -10     # HST (no DST)
}