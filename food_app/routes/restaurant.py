from flask import Blueprint, request
from flask_jwt_extended import jwt_staff_required, get_jwt_identity

from food_app.controllers import RestaurantController
from food_app.models import User

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/<int:restaurant_id>', methods=['PUT'])
@jwt_staff_required
def update_restaurant(restaurant_id):
    """Owner cập nhật restaurant"""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.update_restaurant(restaurant_id, data, current_user)

@restaurant_bp.route('/<int:restaurant_id>/approve', methods=['POST'])
@jwt_staff_required
def approve_restaurant(restaurant_id):
    """Admin phê duyệt restaurant"""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.approve_restaurant(restaurant_id, data, current_user)

@restaurant_bp.route('/pending', methods=['GET'])
@jwt_staff_required
def get_pending_restaurants():
    """Admin xem restaurant chờ phê duyệt"""
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.get_pending_restaurants(current_user)

@restaurant_bp.route('/', methods=['POST'])
@jwt_staff_required
def create_restaurant():
    """Owner tạo restaurant mới"""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.create_restaurant(data, current_user)

@restaurant_bp.route('/', methods=['GET'])
@jwt_staff_required
def get_my_restaurant():
    """Owner lấy thông tin restaurant của mình"""
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.get_my_restaurant(current_user)

@restaurant_bp.route('/', methods=['PUT'])
@jwt_staff_required
def update_restaurant():
    """Owner cập nhật restaurant"""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.update_restaurant(data, current_user)

@restaurant_bp.route('/invite', methods=['POST'])
@jwt_staff_required
def invite_staff():
    """Owner mời staff/manager"""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.invite_staff(data, current_user)

@restaurant_bp.route('/invitations', methods=['GET'])
@jwt_staff_required
def get_pending_invitations():
    """Lấy danh sách lời mời đang chờ"""
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.get_pending_invitations(current_user)

@restaurant_bp.route('/invitations/received', methods=['GET'])
@jwt_staff_required
def get_received_invitations():
    """Lấy danh sách lời mời đã nhận"""
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.get_received_invitations(current_user)

@restaurant_bp.route('/invitations/<int:invitation_id>/respond', methods=['POST'])
@jwt_staff_required
def respond_to_invitation(invitation_id):
    """Phản hồi lời mời"""
    data = request.get_json()
    action = data.get('action')  # 'accept' hoặc 'reject'
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.respond_to_invitation(invitation_id, action, current_user)

@restaurant_bp.route('/staff', methods=['GET'])
@jwt_staff_required
def get_restaurant_staff():
    """Lấy danh sách staff/manager"""
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.get_restaurant_staff(current_user)