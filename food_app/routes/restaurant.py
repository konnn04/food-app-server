from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from food_app.utils.decorators import jwt_staff_required
from flasgger import swag_from

from food_app.controllers import RestaurantController
from food_app.models import User

restaurant_bp = Blueprint('restaurant', __name__)

# Public routes (không cần authentication)
@restaurant_bp.route('/public', methods=['GET'])
@swag_from({'tags': ['Restaurant'], 'summary': 'Public list restaurants with pagination and geo filter', 'parameters': [
    {'in': 'query', 'name': 'q', 'schema': {'type': 'string'}},
    {'in': 'query', 'name': 'page', 'schema': {'type': 'integer'}},
    {'in': 'query', 'name': 'per_page', 'schema': {'type': 'integer'}},
    {'in': 'query', 'name': 'lat', 'schema': {'type': 'number', 'format': 'float'}},
    {'in': 'query', 'name': 'lon', 'schema': {'type': 'number', 'format': 'float'}},
    {'in': 'query', 'name': 'max_km', 'schema': {'type': 'number', 'format': 'float'}}
]})
def list_restaurants_public():
    """Danh sách nhà hàng công khai"""
    from food_app.controllers import RestaurantController
    return RestaurantController.list_restaurants()

@restaurant_bp.route('/<int:restaurant_id>/detail', methods=['GET'])
@swag_from({'tags': ['Restaurant'], 'summary': 'Get restaurant detail with additional info'})
def get_restaurant_detail_public(restaurant_id):
    """Lấy chi tiết nhà hàng với thông tin bổ sung"""
    from food_app.controllers import RestaurantController
    return RestaurantController.get_restaurant_detail(restaurant_id)