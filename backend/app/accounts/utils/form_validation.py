import re

# Validation function for the username
def validation_username(username):
    # Check if the username matches the pattern: only alphanumeric characters and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        # If it doesn't match, return a response indicating the invalid format
        return {'response': 'Invalid username format. Only alphanumeric characters and underscore (_) are allowed.'}
    # If the username is valid, return None (no error)
    return None

# Validation function for the email
def validation_email(email):
    # Compile a regular expression pattern for a valid email format
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', re.IGNORECASE)
    # Check if the email matches the pattern
    if not email_regex.match(email):
        # If it doesn't match, return a response indicating the invalid format
        return {'response': 'invalid gmail format. backend'}
    # If the email is valid, return None (no error)
    return None

# Validation function for the password
def validation_password(password):
    # Check if the password is at least 8 characters long
    if len(password) < 8:
        return {'response': 'Password must be at least 8 characters long. backend'}
    
    # Check if the password contains at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return {'response': 'Password must contain at least one uppercase letter. backend'}
    
    # Check if the password contains at least one number
    if not re.search(r'\d', password):
        return {'response': 'Password must contain at least one number. backend'}
    
    # Check if the password contains at least one special character
    if not re.search(r'[!@#$%^&*]', password):
        return {'response': 'Password must contain at least one special character. backend'}
    
    # If all checks pass, return None (no error)
    return None
