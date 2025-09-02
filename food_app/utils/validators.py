import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 6

def validate_phone(phone):
    pattern = r'^(0|\+84)[3-9][0-9]{8}$'
    return re.match(pattern, phone) is not None

def normalize_phone(phone):
    if not phone:
        return phone
    
    phone = re.sub(r'\D', '', phone)
    
    if phone.startswith('84'):
        phone = '0' + phone[2:]
    
    return phone