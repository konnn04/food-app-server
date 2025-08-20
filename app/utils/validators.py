import re

def validate_email(email):
    """Kiểm tra định dạng email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Kiểm tra mật khẩu có ít nhất 6 ký tự"""
    return len(password) >= 6

def validate_phone(phone):
    """Kiểm tra định dạng số điện thoại Việt Nam"""
    pattern = r'^(0|\+84)[3-9][0-9]{8}$'
    return re.match(pattern, phone) is not None