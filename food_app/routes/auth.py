from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from food_app.controllers.auth_controller import AuthController
from food_app.dao import UserDAO, CustomerDAO
from food_app.utils.decorators import require_role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/staff/login', methods=['POST'])
def staff_login():
    """Đăng nhập cho staff/manager/admin với JWT"""
    data = request.get_json()
    return AuthController.staff_login(data)

@auth_bp.route('/staff/register', methods=['POST'])
@require_role('manager')
def create_staff():
    """Tạo tài khoản staff (chỉ manager+ mới được tạo)"""
    data = request.get_json()
    # Lấy current_user từ JWT token (cần implement trong controller)
    current_user = None  # TODO: Get from JWT
    return AuthController.create_staff(data, current_user)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Lấy thông tin profile từ JWT token"""
    identity = get_jwt_identity()
    user_type = identity.get('user_type')
    user_id = identity.get('user_id')

    if user_type == 'customer':
        user = CustomerDAO.get_customer_by_id(user_id)
    else:  # staff
        user = UserDAO.get_user_by_id(user_id)

    return AuthController.get_profile(user)

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Cập nhật thông tin profile"""
    identity = get_jwt_identity()
    user_type = identity.get('user_type')
    user_id = identity.get('user_id')
    data = request.get_json()

    if user_type == 'customer':
        user = CustomerDAO.get_customer_by_id(user_id)
    else:  # staff
        user = UserDAO.get_user_by_id(user_id)

    return AuthController.update_profile(user, data)

@auth_bp.route('/customer/send-otp', methods=['POST'])
def send_customer_otp():
    """Gửi OTP cho khách hàng qua SMS"""
    data = request.get_json()
    return AuthController.send_customer_otp(data)

@auth_bp.route('/customer/verify-otp', methods=['POST'])
def verify_customer_otp():
    """Xác thực OTP cho khách hàng và cấp JWT"""
    data = request.get_json()
    return AuthController.verify_customer_otp(data)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Làm mới access token bằng refresh token"""
    identity = get_jwt_identity()
    return AuthController.refresh_token(identity)