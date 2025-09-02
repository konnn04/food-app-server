from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from food_app.utils.decorators import jwt_staff_required
from flasgger import swag_from

from food_app.controllers import RestaurantController
from food_app.models import User

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/<int:restaurant_id>', methods=['PUT'])
@jwt_staff_required
@swag_from({'tags': ['Restaurant'], 'summary': 'Owner update restaurant by id'})
def update_restaurant_by_id(restaurant_id):
    """Owner cập nhật restaurant"""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.update_restaurant(restaurant_id, data, current_user)

@restaurant_bp.route('/<int:restaurant_id>/approve', methods=['POST'])
@jwt_staff_required
@swag_from({'tags': ['Restaurant'], 'summary': 'Admin approve restaurant'})
def approve_restaurant(restaurant_id):
    """Admin phê duyệt restaurant"""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.approve_restaurant(restaurant_id, data, current_user)

@restaurant_bp.route('/pending', methods=['GET'])
@jwt_staff_required
@swag_from({'tags': ['Restaurant'], 'summary': 'List pending restaurants'})
def get_pending_restaurants():
    """Admin xem restaurant chờ phê duyệt"""
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.get_pending_restaurants(current_user)

@restaurant_bp.route('/', methods=['POST'])
@jwt_staff_required
@swag_from({'tags': ['Restaurant'], 'summary': 'Owner create restaurant'})
def create_restaurant():
    """Owner tạo restaurant mới"""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.create_restaurant(data, current_user)

@restaurant_bp.route('/', methods=['GET'])
@jwt_staff_required
@swag_from({'tags': ['Restaurant'], 'summary': 'Owner get my restaurant'})
def get_my_restaurant():
    """Owner lấy thông tin restaurant của mình"""
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.get_my_restaurant(current_user)

@restaurant_bp.route('/public', methods=['GET'])
@swag_from({'tags': ['Restaurant'], 'summary': 'Public list restaurants with pagination and geo filter', 'parameters': [
    {'in': 'query', 'name': 'q', 'schema': {'type': 'string'}},
    {'in': 'query', 'name': 'page', 'schema': {'type': 'integer'}},
    {'in': 'query', 'name': 'per_page', 'schema': {'type': 'integer'}},
    {'in': 'query', 'name': 'lat', 'schema': {'type': 'number', 'format': 'float'}},
    {'in': 'query', 'name': 'lon', 'schema': {'type': 'number', 'format': 'float'}},
    {'in': 'query', 'name': 'max_km', 'schema': {'type': 'number', 'format': 'float'}}
]})
def public_list_restaurants():
    from food_app.controllers import RestaurantController
    return RestaurantController.list_restaurants()

@restaurant_bp.route('/', methods=['PUT'])
@jwt_staff_required
@swag_from({'tags': ['Restaurant'], 'summary': 'Owner update my restaurant'})
def update_my_restaurant():
    """Owner cập nhật restaurant"""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.update_restaurant(data, current_user)

@restaurant_bp.route('/staff', methods=['POST'])
@jwt_staff_required
@swag_from({'tags': ['Restaurant'], 'summary': 'Add staff to restaurant'})
def add_staff():
    """Owner/manager thêm staff/manager vào nhà hàng"""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.add_staff(data, current_user)

@restaurant_bp.route('/staff/<int:user_id>', methods=['DELETE'])
@jwt_staff_required
@swag_from({'tags': ['Restaurant'], 'summary': 'Remove staff from restaurant'})
def remove_staff(user_id):
    """Owner/manager xóa nhân viên khỏi nhà hàng"""
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.remove_staff(user_id, current_user)

# Invitation endpoints removed

@restaurant_bp.route('/staff', methods=['GET'])
@jwt_staff_required
@swag_from({'tags': ['Restaurant'], 'summary': 'List restaurant staff'})
def get_restaurant_staff():
    """Lấy danh sách staff/manager"""
    current_user = User.query.get(get_jwt_identity())
    return RestaurantController.get_restaurant_staff(current_user)