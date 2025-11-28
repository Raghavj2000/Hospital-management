import re
from datetime import datetime, date, time

def parse_date(date_string):
    """Parse date string to date object"""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        return None

def parse_time(time_string):
    """Parse time string to time object"""
    try:
        return datetime.strptime(time_string, '%H:%M').time()
    except ValueError:
        return None
