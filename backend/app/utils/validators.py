import re
from datetime import datetime, date, time

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True
    pattern = r'^\+?[\d\s\-()]{10,}$'
    return re.match(pattern, phone) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Valid password"

def validate_date(date_string):
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_time(time_string):
    """Validate time format (HH:MM)"""
    try:
        datetime.strptime(time_string, '%H:%M')
        return True
    except ValueError:
        return False

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    return missing_fields

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
