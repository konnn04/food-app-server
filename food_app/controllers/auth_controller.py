from food_app.dao import UserDAO, CustomerDAO, OTPDAO
from food_app.utils.jwt_service import generate_tokens
from food_app.utils.sms import send_otp_sms
from werkzeug.security import generate_password_hash
from food_app.utils.validators import validate_phone, validate_password, validate_email, normalize_phone
from food_app.utils.responses import success_response, error_response
from food_app.models.base_user import BaseUser
from datetime import datetime

class AuthController:
    @staticmethod
    def staff_login(data):
        """Đăng nhập cho staff/manager/admin với JWT"""
        try:
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return error_response('Thiếu tên đăng nhập hoặc mật khẩu', 400)

            # Tìm user
            user = UserDAO.get_user_by_credentials(username)

            if not user:
                return error_response('Tài khoản không tồn tại', 401)

            if not user.check_password(password):
                return error_response('Mật khẩu không đúng', 401)

            if not user.is_active:
                return error_response('Tài khoản đã bị khóa', 401)

            # Cập nhật last login
            UserDAO.update_last_login(user)

            # Tạo JWT tokens
            tokens = generate_tokens(user.id, 'staff', user.role)

            response_data = {
                'user': user.to_dict(),
                'tokens': tokens
            }

            return success_response('Đăng nhập thành công', response_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

   
    @staticmethod
    def get_profile(user):
        """Lấy thông tin profile"""
        try:
            return success_response('Lấy thông tin thành công', user.to_dict())
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def update_profile(user, data):
        """Cập nhật thông tin profile"""
        try:
            update_data = {}

            if 'first_name' in data:
                update_data['first_name'] = data['first_name']
            if 'last_name' in data:
                update_data['last_name'] = data['last_name']
            if 'address' in data:
                update_data['address'] = data['address']
            if 'email' in data:
                update_data['email'] = data['email']
            if 'gender' in data:
                update_data['gender'] = data['gender']
            if 'date_of_birth' in data:
                try:
                    update_data['date_of_birth'] = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    return error_response('Ngày sinh không hợp lệ (định dạng YYYY-MM-DD)', 400)

            updated_user = UserDAO.update_user(user, update_data)

            return success_response('Cập nhật thành công', updated_user.to_dict())

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def send_customer_otp(data):
        phone = data.get('phone')
        if not phone:
            return error_response('Thiếu số điện thoại', 400)

        if not validate_phone(phone):
            return error_response('Số điện thoại không hợp lệ', 400)

        normalized_phone = normalize_phone(phone)
        existing_user = BaseUser.query.filter_by(phone=normalized_phone).first()
        
        if existing_user and existing_user.user_type == 'staff':
            return error_response('Số điện thoại đã được đăng ký bởi tài khoản nhân viên', 400)

        otp_code = OTPDAO.generate_otp_for_phone(normalized_phone)
        return success_response('OTP đã được tạo', {'otp': otp_code}, 200)

    @staticmethod
    def verify_customer_otp(data):
        phone = data.get('phone')
        otp_code = data.get('otp_code')

        if not phone or not otp_code:
            return error_response('Thiếu số điện thoại hoặc mã OTP', 400)

        normalized_phone = normalize_phone(phone)
        
        if not OTPDAO.verify_otp(normalized_phone, otp_code):
            return error_response('Mã OTP không đúng hoặc đã hết hạn', 400)

        customer = CustomerDAO.get_customer_by_phone(normalized_phone)
        is_new = False

        if not customer:
            customer_data = {'phone': normalized_phone, 'is_need_update': True}
            customer = CustomerDAO.create_customer(customer_data)
            is_new = True

        CustomerDAO.update_customer(customer, {'last_login': datetime.utcnow()})
        tokens = generate_tokens(customer.id, 'customer')

        response_data = {
            'customer': customer.to_dict(),
            'tokens': tokens,
            'is_new': is_new
        }

        return success_response('Đăng nhập thành công', response_data)

    @staticmethod
    def refresh_token(identity):
        """Làm mới access token bằng refresh token"""
        try:
            from flask_jwt_extended import create_access_token
            access_token = create_access_token(identity=identity)

            return success_response('Làm mới token thành công', {
                'access_token': access_token,
                'token_type': 'Bearer'
            })

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def create_owner(data):
        """Tạo tài khoản owner mới (không tạo restaurant ngay)"""
        try:
            required_fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'password', 'username', 'gender']
            for field in required_fields:
                if not data.get(field):
                    return error_response(f'Thiếu thông tin bắt buộc: {field}', 400)

            if not validate_phone(data['phone']):
                return error_response('Số điện thoại không hợp lệ', 400)

            if not validate_email(data['email']):
                return error_response('Email không hợp lệ', 400)

            # Kiểm tra tồn tại
            if UserDAO.get_user_by_username(data['username']):
                return error_response('Tên đăng nhập đã tồn tại', 400)

            if UserDAO.get_user_by_phone(data['phone']):
                return error_response('Số điện thoại đã được sử dụng', 400)

            if UserDAO.get_user_by_email(data['email']):
                return error_response('Email đã được sử dụng', 400)

            password_hash = generate_password_hash(data['password'])
            user_data = {
                'username': data['username'],
                'phone': data['phone'],
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'role': 'owner', 
                'gender': data['gender'],
                'address': data['address'],
                'password_hash': password_hash
            }

            user = UserDAO.create_user(user_data)

            response_data = user.to_dict()
            response_data['next_step'] = 'create_restaurant'  # Hướng dẫn bước tiếp theo

            return success_response('Tạo tài khoản owner thành công. Vui lòng tạo nhà hàng của bạn.', response_data, 201)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

