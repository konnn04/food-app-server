from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from app import db
from app.models.customer import Customer
from app.models.user import User
from app.models.otp import OTP
from app.utils.validators import validate_phone, validate_password, validate_email
from app.utils.responses import success_response, error_response
from app.utils.jwt_service import generate_tokens
from app.utils.sms import send_otp_sms
from app.utils.decorators import require_role
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/staff/login', methods=['POST'])
def staff_login():
    """Đăng nhập cho staff/manager/admin với JWT"""
    try:
        data = request.get_json()
        username = data.get('username')  # có thể là username, email hoặc phone
        password = data.get('password')
        
        if not username or not password:
            return error_response('Thiếu tên đăng nhập hoặc mật khẩu', 400)
        
        # Tìm theo username hoặc email hoặc phone
        user = User.query.filter(
            (User.username == username) | 
            (User.email == username) | 
            (User.phone == username)
        ).first()
        
        if not user:
            return error_response('Tài khoản không tồn tại', 401)
        
        if not user.check_password(password):
            return error_response('Mật khẩu không đúng', 401)
        
        if not user.is_active:
            return error_response('Tài khoản đã bị khóa', 401)
        
        # Cập nhật last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Tạo JWT tokens
        tokens = generate_tokens(user.id, 'staff', user.role)
        
        # Chuẩn bị response
        response_data = {
            'user': user.to_dict(),
            'tokens': tokens
        }
        
        return success_response('Đăng nhập thành công', response_data)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@auth_bp.route('/staff/register', methods=['POST'])
@require_role('manager')
def create_staff():
    """Tạo tài khoản staff (chỉ manager+ mới được tạo)"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['username', 'password', 'phone', 'full_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'Thiếu thông tin: {field}', 400)
        
        if data['role'] not in ['staff', 'manager']:
            return error_response('Vai trò không hợp lệ', 400)
        
        if not validate_password(data['password']):
            return error_response('Mật khẩu phải có ít nhất 6 ký tự', 400)
        
        if not validate_phone(data['phone']):
            return error_response('Số điện thoại không hợp lệ', 400)
        
        # Kiểm tra tồn tại
        if User.query.filter_by(username=data['username']).first():
            return error_response('Tên đăng nhập đã tồn tại', 400)
        
        if User.query.filter_by(phone=data['phone']).first():
            return error_response('Số điện thoại đã được sử dụng', 400)
        
        if data.get('email') and User.query.filter_by(email=data['email']).first():
            return error_response('Email đã được sử dụng', 400)
        
        # Tạo user
        user = User(
            username=data['username'],
            phone=data['phone'],
            email=data.get('email'),
            full_name=data['full_name'],
            role=data['role'],
            restaurant_id=data.get('restaurant_id'),
            gender=data.get('gender'),
            address=data.get('address')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return success_response('Tạo tài khoản thành công', user.to_dict(), 201)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Lấy thông tin profile từ JWT token"""
    try:
        identity = get_jwt_identity()
        user_type = identity.get('user_type')
        user_id = identity.get('user_id')
        
        if user_type == 'customer':
            user = Customer.query.get(user_id)
        else:  # staff
            user = User.query.get(user_id)
        
        if not user:
            return error_response('Người dùng không tồn tại', 404)
        
        return success_response('Lấy thông tin thành công', user.to_dict())
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Cập nhật thông tin profile"""
    try:
        identity = get_jwt_identity()
        user_type = identity.get('user_type')
        user_id = identity.get('user_id')
        
        data = request.get_json()
        
        if user_type == 'customer':
            user = Customer.query.get(user_id)
        else:  # staff
            user = User.query.get(user_id)
        
        if not user:
            return error_response('Người dùng không tồn tại', 404)
        
        # Cập nhật thông tin được phép
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'address' in data:
            user.address = data['address']
        if 'email' in data:
            user.email = data['email']
        if 'gender' in data:
            user.gender = data['gender']
        if 'date_of_birth' in data:
            try:
                user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('Ngày sinh không hợp lệ (định dạng YYYY-MM-DD)', 400)
        
        db.session.commit()
        
        return success_response('Cập nhật thành công', user.to_dict())
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@auth_bp.route('/customer/send-otp', methods=['POST'])
def send_customer_otp():
    """Gửi OTP cho khách hàng qua SMS"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone or not validate_phone(phone):
            return error_response('Số điện thoại không hợp lệ', 400)
        
        # Tạo OTP mới trong bảng OTP
        otp_code = OTP.generate_for_phone(phone)
        
        # Gửi SMS
        sms_sent = send_otp_sms(phone, otp_code)
        
        if sms_sent:
            return success_response('OTP đã được gửi đến số điện thoại của bạn')
        else:
            # Trong môi trường dev, trả về OTP
            return success_response('OTP đã được tạo', {'otp': otp_code})
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@auth_bp.route('/customer/verify-otp', methods=['POST'])
def verify_customer_otp():
    """Xác thực OTP cho khách hàng và cấp JWT"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        otp_code = data.get('otp_code')
        
        if not phone or not otp_code:
            return error_response('Thiếu số điện thoại hoặc mã OTP', 400)
        
        # Xác thực OTP
        if not OTP.verify(phone, otp_code):
            return error_response('Mã OTP không đúng hoặc đã hết hạn', 400)
        
        # Tìm hoặc tạo customer
        customer = Customer.query.filter_by(phone=phone).first()
        if not customer:
            # Tạo mới customer nếu chưa tồn tại
            customer = Customer(
                phone=phone,
                full_name=data.get('full_name', ''),
                address=data.get('address', ''),
                gender=data.get('gender', 'male')
            )
            db.session.add(customer)
        
        # Cập nhật thông tin nếu cần
        if data.get('full_name') and not customer.full_name:
            customer.full_name = data['full_name']
        if data.get('address') and not customer.address:
            customer.address = data['address']
        if data.get('gender'):
            customer.gender = data['gender']
        
        # Cập nhật last login
        customer.last_login = datetime.utcnow()
        db.session.commit()
        
        # Tạo JWT tokens
        tokens = generate_tokens(customer.id, 'customer')
        
        # Chuẩn bị response
        response_data = {
            'customer': customer.to_dict(),
            'tokens': tokens,
            'is_new': not bool(customer.full_name)  # Kiểm tra xem có phải khách hàng mới không
        }
        
        return success_response('Đăng nhập thành công', response_data)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Làm mới access token bằng refresh token"""
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        
        return success_response('Làm mới token thành công', {
            'access_token': access_token,
            'token_type': 'Bearer'
        })
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)