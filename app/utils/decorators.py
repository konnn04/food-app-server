from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
from app.models.customer import Customer
from app.utils.responses import error_response
from app.utils.jwt_service import get_user_id_from_jwt, get_user_type_from_jwt, get_role_from_jwt

def jwt_customer_required(f):
    """Decorator yêu cầu JWT của customer"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_type = get_user_type_from_jwt()
            user_id = get_user_id_from_jwt()
            
            if not user_type or user_type != 'customer':
                return error_response('Không có quyền truy cập', 403)
            
            customer = Customer.query.get(user_id)
            if not customer:
                return error_response('Khách hàng không tồn tại', 404)
            
            # Thêm customer vào kwargs
            kwargs['current_customer'] = customer
            return f(*args, **kwargs)
        except Exception as e:
            return error_response(f'Lỗi xác thực: {str(e)}', 401)
    return decorated_function

def jwt_staff_required(f):
    """Decorator yêu cầu JWT của staff/manager/admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_type = get_user_type_from_jwt()
            user_id = get_user_id_from_jwt()
            
            if not user_type or user_type != 'staff':
                return error_response('Không có quyền truy cập', 403)
            
            user = User.query.get(user_id)
            if not user:
                return error_response('Người dùng không tồn tại', 404)
            
            # Thêm user vào kwargs
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        except Exception as e:
            return error_response(f'Lỗi xác thực: {str(e)}', 401)
    return decorated_function

def admin_required(f):
    """Decorator yêu cầu JWT của admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_type = get_user_type_from_jwt()
            user_id = get_user_id_from_jwt()
            role = get_role_from_jwt()
            
            if not user_type or user_type != 'staff' or role != 'admin':
                return error_response('Không có quyền admin', 403)
            
            user = User.query.get(user_id)
            if not user or user.role != 'admin':
                return error_response('Không có quyền admin', 403)
            
            return f(*args, **kwargs)
        except Exception as e:
            return error_response(f'Lỗi xác thực: {str(e)}', 401)
    return decorated_function

def manager_required(f):
    """Decorator yêu cầu JWT của manager hoặc admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_type = get_user_type_from_jwt()
            user_id = get_user_id_from_jwt()
            role = get_role_from_jwt()
            
            if not user_type or user_type != 'staff':
                return error_response('Không có quyền quản lý', 403)
            
            if role not in ['manager', 'admin']:
                return error_response('Không có quyền quản lý', 403)
            
            user = User.query.get(user_id)
            if not user or user.role not in ['manager', 'admin']:
                return error_response('Không có quyền quản lý', 403)
            
            # Thêm user vào kwargs
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        except Exception as e:
            return error_response(f'Lỗi xác thực: {str(e)}', 401)
    return decorated_function

# Decorator cũ giữ lại để tương thích
def require_role(required_role):
    """Decorator yêu cầu quyền tối thiểu cho staff"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = request.headers.get('X-User-ID')
            
            if not user_id:
                return error_response('Chưa đăng nhập', 401)
            
            user = User.query.get(user_id)
            if not user:
                return error_response('Người dùng không tồn tại', 401)
            
            if not user.has_role(required_role):
                return error_response('Không có quyền truy cập', 403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator