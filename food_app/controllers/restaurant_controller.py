from food_app.dao import RestaurantDAO, UserDAO
from food_app.utils.responses import success_response, error_response
from flask_jwt_extended import get_jwt_identity
from food_app.models.invitation import Invitation
from food_app import db

class RestaurantController:
    @staticmethod
    def create_restaurant(data, current_user):
        """Owner tạo restaurant mới (duy nhất 1)"""
        try:
            # Kiểm tra quyền owner
            if current_user.role != 'owner':
                return error_response('Chỉ owner mới có thể tạo nhà hàng', 403)

            # Kiểm tra owner đã có restaurant chưa
            if current_user.owned_restaurant:
                return error_response('Bạn đã có nhà hàng rồi. Mỗi owner chỉ được tạo 1 nhà hàng.', 400)

            # Validation
            required_fields = ['name', 'address', 'phone', 'email', 'tax_code']
            for field in required_fields:
                if not data.get(field):
                    return error_response(f'Thiếu thông tin bắt buộc: {field}', 400)

            # Tạo restaurant data
            restaurant_data = {
                'name': data['name'],
                'address': data['address'],
                'phone': data['phone'],
                'email': data['email'],
                'description': data.get('description'),
                'image_url': data.get('image_url'),
                'opening_hours': data.get('opening_hours', {}),
                'tax_code': data['tax_code'],
                'owner_id': current_user.id
            }

            restaurant = RestaurantDAO.create_restaurant(restaurant_data)
            
            return success_response('Tạo nhà hàng thành công', restaurant.to_dict(), 201)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_my_restaurant(current_user):
        """Lấy thông tin restaurant của owner"""
        try:
            if current_user.role != 'owner':
                return error_response('Chỉ owner mới có quyền xem', 403)

            if not current_user.owned_restaurant:
                return error_response('Bạn chưa tạo nhà hàng. Vui lòng tạo nhà hàng trước.', 404)

            restaurant = current_user.owned_restaurant
            
            return success_response('Lấy thông tin nhà hàng thành công', restaurant.to_dict())

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def update_restaurant(data, current_user):
        """Owner cập nhật restaurant của mình"""
        try:
            if current_user.role != 'owner':
                return error_response('Chỉ owner mới có quyền cập nhật', 403)

            if not current_user.owned_restaurant:
                return error_response('Bạn chưa tạo nhà hàng', 404)

            restaurant = current_user.owned_restaurant

            # Cập nhật dữ liệu
            update_data = {}
            allowed_fields = [
                'name', 'address', 'phone', 'email', 'description', 
                'image_url', 'opening_hours', 'is_active'
            ]
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]

            updated_restaurant = RestaurantDAO.update_restaurant(restaurant, update_data)
            
            return success_response('Cập nhật nhà hàng thành công', updated_restaurant.to_dict())

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def invite_staff(data, current_user):
        """Owner mời staff/manager"""
        try:
            if not current_user.can_invite_staff():
                return error_response('Bạn không có quyền mời nhân viên', 403)

            if not current_user.owned_restaurant:
                return error_response('Bạn chưa tạo nhà hàng', 404)

            # Validation
            username = data.get('username')
            role = data.get('role')
            message = data.get('message', '')

            if not username:
                return error_response('Thiếu username của người được mời', 400)

            if role not in ['staff', 'manager']:
                return error_response('Vai trò phải là staff hoặc manager', 400)

            # Kiểm tra user tồn tại
            invited_user = UserDAO.get_user_by_username(username)
            if not invited_user:
                return error_response('Không tìm thấy user với username này', 404)

            # Kiểm tra user đã thuộc restaurant nào chưa
            if invited_user.restaurant_id:
                return error_response('User này đã thuộc một nhà hàng khác', 400)

            # Kiểm tra đã mời chưa
            existing_invitation = Invitation.query.filter_by(
                restaurant_id=current_user.owned_restaurant.id,
                invited_username=username,
                status='pending'
            ).first()

            if existing_invitation:
                return error_response('Đã gửi lời mời cho user này rồi', 400)

            # Tạo lời mời
            invitation = Invitation(
                restaurant_id=current_user.owned_restaurant.id,
                invited_username=username,
                invited_email=invited_user.email,
                role=role,
                invited_by=current_user.id,
                message=message
            )

            db.session.add(invitation)
            db.session.commit()

            return success_response('Gửi lời mời thành công', invitation.to_dict(), 201)

        except Exception as e:
            db.session.rollback()
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_pending_invitations(current_user):
        """Lấy danh sách lời mời đang chờ (owner xem)"""
        try:
            if current_user.role != 'owner' or not current_user.owned_restaurant:
                return error_response('Không có quyền truy cập', 403)

            invitations = current_user.get_pending_invitations()
            invitations_data = [inv.to_dict() for inv in invitations]

            return success_response('Lấy danh sách lời mời thành công', invitations_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_received_invitations(current_user):
        """Lấy danh sách lời mời đã nhận (staff/manager xem)"""
        try:
            invitations = current_user.get_received_invitations()
            invitations_data = [inv.to_dict() for inv in invitations]

            return success_response('Lấy danh sách lời mời thành công', invitations_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def respond_to_invitation(invitation_id, action, current_user):
        """Staff/Manager phản hồi lời mời"""
        try:
            invitation = Invitation.query.get(invitation_id)
            if not invitation:
                return error_response('Không tìm thấy lời mời', 404)

            # Kiểm tra quyền
            if invitation.invited_username != current_user.username:
                return error_response('Bạn không có quyền phản hồi lời mời này', 403)

            if invitation.status != 'pending':
                return error_response('Lời mời này đã được xử lý', 400)

            if action == 'accept':
                invitation.accept(current_user)
                message = f'Đã chấp nhận lời mời làm {invitation.role} tại {invitation.restaurant.name}'
            elif action == 'reject':
                invitation.reject()
                message = 'Đã từ chối lời mời'
            else:
                return error_response('Hành động không hợp lệ', 400)

            db.session.commit()

            return success_response(message, invitation.to_dict())

        except Exception as e:
            db.session.rollback()
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_restaurant_staff(current_user):
        """Lấy danh sách staff/manager của restaurant"""
        try:
            if current_user.role == 'owner':
                restaurant = current_user.owned_restaurant
            elif current_user.role in ['manager', 'staff']:
                restaurant = current_user.restaurant
            else:
                return error_response('Không có quyền truy cập', 403)

            if not restaurant:
                return error_response('Không tìm thấy nhà hàng', 404)

            staff_list = [user.to_dict() for user in restaurant.staff_users if user.role in ['staff', 'manager']]

            return success_response('Lấy danh sách nhân viên thành công', staff_list)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)