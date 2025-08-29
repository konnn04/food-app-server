from food_app.dao import UserDAO, CustomerDAO, OTPDAO
from food_app.utils.jwt_service import generate_tokens
from food_app.utils.sms import send_otp_sms
from food_app.utils.validators import validate_phone, validate_password, validate_email
from food_app.utils.responses import success_response, error_response
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
    def create_staff(data, current_user):
        """Tạo tài khoản staff (chỉ manager+ mới được tạo)"""
        try:
            # Validation
            required_fields = ['username', 'password', 'phone', 'first_name', 'last_name', 'role']
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
            if UserDAO.get_user_by_username(data['username']):
                return error_response('Tên đăng nhập đã tồn tại', 400)

            if UserDAO.get_user_by_phone(data['phone']):
                return error_response('Số điện thoại đã được sử dụng', 400)

            if data.get('email') and UserDAO.get_user_by_email(data['email']):
                return error_response('Email đã được sử dụng', 400)

            # Tạo user data
            user_data = {
                'username': data['username'],
                'phone': data['phone'],
                'email': data.get('email'),
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'role': data['role'],
                'restaurant_id': data.get('restaurant_id'),
                'gender': data.get('gender', 'male'),
                'address': data.get('address'),
                'user_type': 'staff'
            }

            user = UserDAO.create_user(user_data)
            user.set_password(data['password'])

            return success_response('Tạo tài khoản thành công', user.to_dict(), 201)

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
        """Gửi OTP cho khách hàng qua SMS"""
        try:
            phone = data.get('phone')

            if not phone or not validate_phone(phone):
                return error_response('Số điện thoại không hợp lệ', 400)

            # Tạo OTP mới
            otp_code = OTPDAO.generate_otp_for_phone(phone)

            # Gửi SMS
            # sms_sent = send_otp_sms(phone, otp_code)

            if False:
                return success_response('OTP đã được gửi đến số điện thoại của bạn')
            else:
                return success_response('OTP đã được tạo', {'otp': otp_code}, 200)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def verify_customer_otp(data):
        """Xác thực OTP cho khách hàng và cấp JWT"""
        try:
            phone = data.get('phone')
            otp_code = data.get('otp_code')

            if not phone or not otp_code:
                return error_response('Thiếu số điện thoại hoặc mã OTP', 400)

            # Xác thực OTP
            if not OTPDAO.verify_otp(phone, otp_code):
                return error_response('Mã OTP không đúng hoặc đã hết hạn', 400)

            # Tìm hoặc tạo customer
            customer = CustomerDAO.get_customer_by_phone(phone)
            is_new = False

            if not customer:
                # Tạo mới customer
                customer_data = {
                    'phone': phone,
                    'first_name': data.get('first_name', ''),
                    'last_name': data.get('last_name', ''),
                    'address': data.get('address', ''),
                    'gender': data.get('gender', 'male'),
                    'user_type': 'customer'
                }
                customer = CustomerDAO.create_customer(customer_data)
                is_new = True
            else:
                # Cập nhật thông tin nếu cần
                update_data = {}
                if data.get('first_name') and not customer.first_name:
                    update_data['first_name'] = data['first_name']
                if data.get('last_name') and not customer.last_name:
                    update_data['last_name'] = data['last_name']
                if data.get('address') and not customer.address:
                    update_data['address'] = data['address']
                if data.get('gender'):
                    update_data['gender'] = data['gender']

                if update_data:
                    customer = CustomerDAO.update_customer(customer, update_data)

            # Cập nhật last login
            CustomerDAO.update_customer(customer, {'last_login': datetime.utcnow()})

            # Tạo JWT tokens
            tokens = generate_tokens(customer.id, 'customer')

            response_data = {
                'customer': customer.to_dict(),
                'tokens': tokens,
                'is_new': is_new
            }

            return success_response('Đăng nhập thành công', response_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

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
