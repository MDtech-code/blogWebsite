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


#! new function 
# Validation function for the bio
def validation_bio(bio):
    if len(bio) > 500:
        return {'response': 'Bio must be 500 characters or less.'}
    return None

# Validation function for the image
def validation_image(image):
    allowed_extensions = ['jpg', 'jpeg', 'png']
    extension = image.name.split('.')[-1].lower()
    if extension not in allowed_extensions:
        return {'response': f'Invalid image format. Allowed formats: {", ".join(allowed_extensions)}.'}
    return None

# Validation function for the gender
def validation_gender(gender):
    allowed_genders = ['M', 'F', 'O']
    if gender not in allowed_genders:
        return {'response': f'Invalid gender. Allowed values: {", ".join(allowed_genders)}.'}
    return None

# Validation function for the age
def validation_age(age):
    if age < 0:
        return {'response': 'Age must be a positive number.'}
    return None

# Validation function for the phone number
def validation_number(number):
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    if not phone_regex.match(number):
        return {'response': 'Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'}
    return None

# Validation function for the Facebook URL
def validation_facebook_url(facebook_url):
    url_regex = re.compile(r'^(https?://)?(www\.)?facebook\.com/.+$', re.IGNORECASE)
    if not url_regex.match(facebook_url):
        return {'response': 'Invalid Facebook URL.'}
    return None

# Validation function for the Instagram URL
def validation_instagram_url(instagram_url):
    url_regex = re.compile(r'^(https?://)?(www\.)?instagram\.com/.+$', re.IGNORECASE)
    if not url_regex.match(instagram_url):
        return {'response': 'Invalid Instagram URL.'}
    return None