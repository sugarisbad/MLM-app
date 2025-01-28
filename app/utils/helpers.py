import re
import logging
from functools import wraps
from flask import current_app
from datetime import datetime

def validate_username(username):
    """
    Validate username based on specific criteria.
    
    Args:
        username (str): Username to validate
    
    Returns:
        bool: True if username is valid, False otherwise
    """
    if not username:
        return False
    
    # Username must be 3-20 characters long
    # Allows letters, numbers, and underscores
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

def validate_password(password):
    """
    Validate password based on security criteria.
    
    Args:
        password (str): Password to validate
    
    Returns:
        bool: True if password meets security requirements, False otherwise
    """
    if not password:
        return False
    
    # At least 8 characters, one uppercase, one lowercase, one number
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
    return bool(re.match(pattern, password))

def log_error(error_message, level=logging.ERROR):
    """
    Log errors with a consistent format.
    
    Args:
        error_message (str): Error message to log
        level (int, optional): Logging level. Defaults to logging.ERROR.
    """
    logger = current_app.logger
    logger.log(level, error_message)

def generate_unique_referral_code(user_id):
    """
    Generate a unique referral code based on user ID.
    
    Args:
        user_id (int): User's unique identifier
    
    Returns:
        str: Unique referral code
    """
    return f"REF-{user_id:06d}"

def is_empty_string(input_string):
    """
    Check if a string is empty.
    
    Args:
        input_string (str): String to check
    
    Returns:
        bool: True if string is empty, False otherwise
    """
    return not input_string.strip()

def is_valid_email(email):
    """
    Validate email address.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if email is valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def get_current_timestamp():
    """
    Get the current timestamp.
    
    Returns:
        int: Current timestamp
    """
    return int(current_app.config['CURRENT_TIMESTAMP'])

def convert_to_bool(input_value):
    """
    Convert a value to a boolean.
    
    Args:
        input_value: Value to convert
    
    Returns:
        bool: Converted boolean value
    """
    return bool(input_value)

def current_year():
    """
    Returns the current year as an integer.
    
    Returns:
        int: Current year
    """
    return datetime.now().year