"""
Utility functions for the application
"""

from datetime import datetime, timezone, timedelta

# 北京时区 UTC+8
BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_now():
    """
    Get current time in Beijing timezone (UTC+8)
    
    Returns:
        datetime: Current datetime in Beijing timezone
    """
    return datetime.now(BEIJING_TZ)


def to_beijing_time(utc_datetime):
    """
    Convert UTC datetime to Beijing time
    
    Args:
        utc_datetime: DateTime object in UTC
    
    Returns:
        datetime: DateTime in Beijing timezone
    """
    if utc_datetime is None:
        return None
    
    # If datetime is naive (no timezone info), assume it's UTC
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    
    return utc_datetime.astimezone(BEIJING_TZ)


def format_beijing_time(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Format datetime to Beijing time string
    
    Args:
        dt: DateTime object
        format_str: Format string for strftime
    
    Returns:
        str: Formatted time string in Beijing timezone
    """
    if dt is None:
        return ''
    
    beijing_time = to_beijing_time(dt)
    return beijing_time.strftime(format_str)
