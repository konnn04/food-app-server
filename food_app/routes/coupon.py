from flask import Blueprint, request
from food_app.controllers.coupon_controller import CouponController
from flasgger import swag_from
from food_app.utils.decorators import jwt_staff_required
from food_app.utils.jwt_service import get_user_id_from_jwt
from food_app.models.user import User

coupon_bp = Blueprint('coupon', __name__)

@coupon_bp.route('/', methods=['POST'], endpoint='coupon_public_create')
@swag_from({'tags': ['Coupon'], 'summary': 'Create coupon', 'requestBody': {'required': True, 'content': {'application/json': {'schema': {'type': 'object'}}}}})
def create_coupon():
    data = request.get_json()
    return CouponController.create_coupon(data)

@coupon_bp.route('/apply', methods=['POST'], endpoint='coupon_apply')
@swag_from({'tags': ['Coupon'], 'summary': 'Apply coupon', 'requestBody': {'required': True, 'content': {'application/json': {'schema': {'type': 'object', 'required': ['code','order_amount'], 'properties': {'code': {'type': 'string'}, 'order_amount': {'type': 'number'}, 'restaurant_id': {'type': 'integer'}, 'food_ids': {'type': 'array', 'items': {'type': 'integer'}}}}}}}})
def apply_coupon():
    data = request.get_json()
    code = data.get('code')
    order_amount = float(data.get('order_amount', 0))
    restaurant_id = data.get('restaurant_id')
    food_ids = data.get('food_ids')
    return CouponController.apply_coupon(code, order_amount, restaurant_id, food_ids)

# Public list
@coupon_bp.route('/', methods=['GET'], endpoint='coupon_public_list')
@swag_from({'tags': ['Coupon'], 'summary': 'Public list coupons'})
def list_coupons():
    return CouponController.list_public(request.args)

@coupon_bp.route('/code/<string:code>', methods=['GET'], endpoint='coupon_get_by_code')
@swag_from({'tags': ['Coupon'], 'summary': 'Get coupon by code', 'parameters': [{'in': 'path', 'name': 'code', 'schema': {'type': 'string'}, 'required': True}]})
def get_coupon_by_code(code):
    return CouponController.get_by_code(code)

# Staff/Owner management
@coupon_bp.route('/restaurant/<int:restaurant_id>', methods=['GET'], endpoint='coupon_list_by_restaurant')
@jwt_staff_required() 
@swag_from({'tags': ['Coupon'], 'summary': 'List coupons by restaurant (staff)', 'parameters': [{'in': 'path', 'name': 'restaurant_id', 'schema': {'type': 'integer'}, 'required': True}]})
def list_coupons_by_restaurant(restaurant_id, current_user):  
    return CouponController.list_by_restaurant(restaurant_id, current_user)

@coupon_bp.route('/restaurant/<int:restaurant_id>', methods=['POST'], endpoint='coupon_staff_create')
@jwt_staff_required()
@swag_from({'tags': ['Coupon'], 'summary': 'Create coupon for restaurant (staff)', 'parameters': [{'in': 'path', 'name': 'restaurant_id', 'schema': {'type': 'integer'}, 'required': True}], 'requestBody': {'required': True, 'content': {'application/json': {'schema': {'type': 'object'}}}}})
def staff_create_coupon(restaurant_id, current_user):
    data = request.get_json()
    return CouponController.staff_create(restaurant_id, data, current_user)

@coupon_bp.route('/<int:coupon_id>', methods=['PUT'], endpoint='coupon_staff_update')
@jwt_staff_required()
@swag_from({'tags': ['Coupon'], 'summary': 'Update coupon (staff)', 'parameters': [{'in': 'path', 'name': 'coupon_id', 'schema': {'type': 'integer'}, 'required': True}], 'requestBody': {'required': True, 'content': {'application/json': {'schema': {'type': 'object'}}}}})
def staff_update_coupon(coupon_id, current_user):  # Nhận current_user từ decorator
    data = request.get_json()
    return CouponController.staff_update(coupon_id, data, current_user)

@coupon_bp.route('/<int:coupon_id>', methods=['DELETE'], endpoint='coupon_staff_delete')
@jwt_staff_required()
@swag_from({'tags': ['Coupon'], 'summary': 'Delete coupon (staff)', 'parameters': [{'in': 'path', 'name': 'coupon_id', 'schema': {'type': 'integer'}, 'required': True}]})
def staff_delete_coupon(coupon_id, current_user):
    return CouponController.staff_delete(coupon_id, current_user)


