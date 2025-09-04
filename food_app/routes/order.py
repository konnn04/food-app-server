from flask import Blueprint, request
from food_app.controllers.order_controller import OrderController
from flasgger import swag_from

order_bp = Blueprint('order', __name__)

@order_bp.route('/', methods=['POST'])
@swag_from({'tags': ['Order'], 'summary': 'Create order', 'responses': {'201': {'description': 'Created'}}})
def create_order():
    """Tạo đơn hàng mới"""
    data = request.get_json()
    return OrderController.create_order(data)

@order_bp.route('/<int:order_id>/', methods=['GET'])
def get_order(order_id):
    """Lấy thông tin một đơn hàng"""
    return OrderController.get_order(order_id)

@order_bp.route('/customer/<int:customer_id>/', methods=['GET'])
def get_customer_orders(customer_id):
    """Lấy danh sách đơn hàng của khách hàng"""
    return OrderController.get_customer_orders(customer_id)

@order_bp.route('/restaurant/<int:restaurant_id>/', methods=['GET'])
def get_restaurant_orders(restaurant_id):
    """Lấy danh sách đơn hàng của nhà hàng"""
    return OrderController.get_restaurant_orders(restaurant_id)

@order_bp.route('/<int:order_id>/status/', methods=['PUT'])
def update_order_status(order_id):
    """Cập nhật trạng thái đơn hàng"""
    data = request.get_json()
    new_status = data.get('status')
    return OrderController.update_order_status(order_id, new_status)

@order_bp.route('/<int:order_id>/cancel/', methods=['POST'])
def cancel_order(order_id):
    data = request.get_json()
    return OrderController.cancel_order(order_id, data)

@order_bp.route('/<int:order_id>/assign-staff/<int:staff_id>/', methods=['PUT'])
def assign_staff_to_order(order_id, staff_id):
    """Gán nhân viên xử lý đơn hàng"""
    data = request.get_json()
    staff_id = data.get('staff_id')
    return OrderController.assign_staff_to_order(order_id, staff_id)