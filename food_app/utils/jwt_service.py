from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from datetime import timedelta

def generate_tokens(user_id, user_type, role=None):
    """
    Tạo access token và refresh token
    Sử dụng user_id làm identity (subject) và lưu thông tin khác trong claims
    """
    # Identity phải là string hoặc số nguyên đơn giản
    identity = str(user_id)
    
    # Thêm thông tin bổ sung vào claims
    additional_claims = {
        'user_type': user_type,  # 'customer' hoặc 'staff'
    }
    
    if role:
        additional_claims['role'] = role
        
    # Access token có thời hạn ngắn hơn
    access_token = create_access_token(
        identity=identity, 
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1)
    )
    
    # Refresh token có thời hạn dài hơn
    refresh_token = create_refresh_token(
        identity=identity,
        additional_claims=additional_claims,
        expires_delta=timedelta(days=30)
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }

def get_user_id_from_jwt():
    """Lấy user_id từ JWT token hiện tại"""
    # Identity bây giờ chính là user_id
    return get_jwt_identity()

def get_user_type_from_jwt():
    """Lấy user_type từ JWT token hiện tại"""
    # Lấy từ claims
    claims = get_jwt()
    return claims.get('user_type')

def get_role_from_jwt():
    """Lấy role từ JWT token hiện tại (nếu có)"""
    # Lấy từ claims
    claims = get_jwt()
    return claims.get('role')
