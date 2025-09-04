from flask import Blueprint, request
from food_app.controllers.staff_controller import StaffController
from food_app.utils.decorators import jwt_required, restaurant_staff_required
from flasgger import swag_from

staff_bp = Blueprint('staff', __name__)

# Food management endpoints
@staff_bp.route('/foods/', methods=['GET'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Get restaurant foods'})
def get_foods():
    """Lấy danh sách món ăn của nhà hàng"""
    return StaffController.get_foods()

@staff_bp.route('/foods/<int:food_id>/', methods=['GET'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Get food details'})
def get_food(food_id):
    """Lấy chi tiết món ăn"""
    return StaffController.get_food(food_id)

@staff_bp.route('/foods/', methods=['POST'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Create new food'})
def create_food():
    """Tạo món ăn mới"""
    data = request.get_json()
    return StaffController.create_food(data)

@staff_bp.route('/foods/<int:food_id>/', methods=['PUT'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Update food'})
def update_food(food_id):
    """Cập nhật món ăn"""
    data = request.get_json()
    return StaffController.update_food(food_id, data)

@staff_bp.route('/foods/<int:food_id>/', methods=['DELETE'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Delete food'})
def delete_food(food_id):
    """Xóa món ăn"""
    return StaffController.delete_food(food_id)

@staff_bp.route('/foods/<int:food_id>/toggle/', methods=['PUT'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Toggle food availability'})
def toggle_food_availability(food_id):
    """Bật/tắt món ăn"""
    return StaffController.toggle_food_availability(food_id)

# Restaurant management endpoints
@staff_bp.route('/restaurant/', methods=['GET'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Get restaurant info'})
def get_restaurant():
    """Lấy thông tin nhà hàng"""
    return StaffController.get_restaurant()

@staff_bp.route('/restaurant/', methods=['PUT'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Update restaurant info'})
def update_restaurant():
    """Cập nhật thông tin nhà hàng"""
    data = request.get_json()
    return StaffController.update_restaurant(data)

@staff_bp.route('/restaurant/hours/', methods=['PUT'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Update opening hours'})
def update_opening_hours():
    """Cập nhật giờ mở cửa"""
    data = request.get_json()
    return StaffController.update_opening_hours(data)

@staff_bp.route('/restaurant/toggle/', methods=['PUT'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Toggle restaurant status'})
def toggle_restaurant_status():
    """Bật/tắt nhà hàng"""
    return StaffController.toggle_restaurant_status()

# Order management endpoints
@staff_bp.route('/orders/', methods=['GET'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Get restaurant orders'})
def get_orders():
    """Lấy danh sách đơn hàng của nhà hàng"""
    status = request.args.get('status')
    return StaffController.get_orders(status)

@staff_bp.route('/orders/<int:order_id>/', methods=['GET'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Get order details'})
def get_order(order_id):
    """Lấy chi tiết đơn hàng"""
    return StaffController.get_order(order_id)

@staff_bp.route('/orders/<int:order_id>/accept/', methods=['PUT'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Accept order'})
def accept_order(order_id):
    """Nhận đơn hàng"""
    return StaffController.accept_order(order_id)

@staff_bp.route('/orders/<int:order_id>/complete/', methods=['PUT'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Complete order'})
def complete_order(order_id):
    """Hoàn thành đơn hàng"""
    return StaffController.complete_order(order_id)

@staff_bp.route('/orders/<int:order_id>/cancel/', methods=['PUT'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Cancel order'})
def cancel_order(order_id):
    """Hủy đơn hàng"""
    data = request.get_json()
    return StaffController.cancel_order(order_id, data)

# Review management endpoints
@staff_bp.route('/reviews/', methods=['GET'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Get restaurant reviews'})
def get_reviews():
    """Lấy đánh giá của nhà hàng"""
    return StaffController.get_reviews()

# Revenue endpoints
@staff_bp.route('/revenue/', methods=['GET'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Get revenue statistics'})
def get_revenue():
    """Lấy thống kê doanh thu"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return StaffController.get_revenue(start_date, end_date)

# Profile endpoints
@staff_bp.route('/profile/', methods=['GET'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Get staff profile'})
def get_profile():
    """Lấy thông tin cá nhân"""
    return StaffController.get_profile()

@staff_bp.route('/profile/', methods=['PUT'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Update staff profile'})
def update_profile():
    """Cập nhật thông tin cá nhân"""
    data = request.get_json()
    return StaffController.update_profile(data)

# Payment endpoints
@staff_bp.route('/payment/deposit/', methods=['POST'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Deposit money (mockup)'})
def deposit_money():
    """Nạp tiền (mockup)"""
    data = request.get_json()
    return StaffController.deposit_money(data)

@staff_bp.route('/payment/withdraw/', methods=['POST'])
@jwt_required
@restaurant_staff_required
@swag_from({'tags': ['Staff'], 'summary': 'Withdraw money (mockup)'})
def withdraw_money():
    """Rút tiền (mockup)"""
    data = request.get_json()
    return StaffController.withdraw_money(data)
