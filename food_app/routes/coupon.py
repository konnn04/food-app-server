from flask import Blueprint, request
from food_app.controllers.coupon_controller import CouponController
from flasgger import swag_from

coupon_bp = Blueprint('coupon', __name__)

@coupon_bp.route('/', methods=['POST'])
@swag_from({'tags': ['Coupon'], 'summary': 'Create coupon'})
def create_coupon():
    data = request.get_json()
    return CouponController.create_coupon(data)

@coupon_bp.route('/apply', methods=['POST'])
@swag_from({'tags': ['Coupon'], 'summary': 'Apply coupon'})
def apply_coupon():
    data = request.get_json()
    code = data.get('code')
    order_amount = float(data.get('order_amount', 0))
    restaurant_id = data.get('restaurant_id')
    food_ids = data.get('food_ids')
    return CouponController.apply_coupon(code, order_amount, restaurant_id, food_ids)


