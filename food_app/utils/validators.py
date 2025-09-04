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

def validate_order_data(data):
    """Validate dữ liệu đơn hàng"""
    if not data:
        return {'valid': False, 'message': 'Dữ liệu không được để trống'}
    
    required_fields = ['delivery_address', 'delivery_phone']
    for field in required_fields:
        if not data.get(field):
            return {'valid': False, 'message': f'Thiếu thông tin {field}'}
    
    # Validate số điện thoại
    phone = data.get('delivery_phone')
    if not phone or len(phone) < 10:
        return {'valid': False, 'message': 'Số điện thoại không hợp lệ'}
    
    return {'valid': True, 'message': 'Dữ liệu hợp lệ'}

def validate_food_data(data):
    """Validate dữ liệu món ăn"""
    if not data:
        return {'valid': False, 'message': 'Dữ liệu không được để trống'}
    
    required_fields = ['name', 'price']
    for field in required_fields:
        if not data.get(field):
            return {'valid': False, 'message': f'Thiếu thông tin {field}'}
    
    # Validate giá
    price = data.get('price')
    if not isinstance(price, (int, float)) or price <= 0:
        return {'valid': False, 'message': 'Giá phải là số dương'}
    
    # Validate tên món
    name = data.get('name')
    if len(name.strip()) < 2:
        return {'valid': False, 'message': 'Tên món phải có ít nhất 2 ký tự'}
    
    return {'valid': True, 'message': 'Dữ liệu hợp lệ'}

def validate_review_data(data):
    """Validate dữ liệu đánh giá"""
    if not data:
        return {'valid': False, 'message': 'Dữ liệu không được để trống'}
    
    required_fields = ['restaurant_id', 'rating']
    for field in required_fields:
        if not data.get(field):
            return {'valid': False, 'message': f'Thiếu thông tin {field}'}
    
    # Validate rating
    rating = data.get('rating')
    if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
        return {'valid': False, 'message': 'Đánh giá phải từ 1-5'}
    
    return {'valid': True, 'message': 'Dữ liệu hợp lệ'}