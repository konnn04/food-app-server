from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from datetime import timedelta

def generate_tokens(user_id, user_type, role=None):
    """Tạo access token và refresh token"""
    identity = {
        'user_id': user_id,
        'user_type': user_type,  # 'customer' hoặc 'staff'
    }
    
    if role:
        identity['role'] = role
        
    # Access token có thời hạn ngắn hơn
    access_token = create_access_token(
        identity=identity, 
        expires_delta=timedelta(hours=1)
    )
    
    # Refresh token có thời hạn dài hơn
    refresh_token = create_refresh_token(
        identity=identity,
        expires_delta=timedelta(days=30)
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }

def get_current_user_identity():
    """Lấy thông tin identity từ JWT token hiện tại"""
    return get_jwt_identity()

def get_user_id_from_jwt():
    """Lấy user_id từ JWT token hiện tại"""
    identity = get_current_user_identity()
    return identity.get('user_id') if identity else None

def get_user_type_from_jwt():
    """Lấy user_type từ JWT token hiện tại"""
    identity = get_current_user_identity()
    return identity.get('user_type') if identity else None

def get_role_from_jwt():
    """Lấy role từ JWT token hiện tại (nếu có)"""
    identity = get_current_user_identity()
    return identity.get('role') if identity else None
