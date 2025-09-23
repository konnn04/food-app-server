from flask import Blueprint, request
from food_app.controllers.customer_controller import CustomerController
from food_app.utils.decorators import jwt_customer_required
from flasgger import swag_from

customer_bp = Blueprint('customer', __name__)

# Profile endpoints
@customer_bp.route('/profile/', methods=['GET'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Get customer profile'})
def get_profile(current_customer): 
    return CustomerController.get_profile(current_customer)

@customer_bp.route('/profile/', methods=['PUT'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Update customer profile'})
def update_profile(current_customer): 
    """Cập nhật thông tin cá nhân"""
    data = request.get_json()
    return CustomerController.update_profile(data, current_customer)

# Cart endpoints
@customer_bp.route('/cart/', methods=['GET'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Get customer cart'})
def get_cart(current_customer):  
    """Lấy giỏ hàng của khách hàng"""
    return CustomerController.get_cart(current_customer)

@customer_bp.route('/cart/add/', methods=['POST'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Add item to cart'})
def add_to_cart(current_customer): 
    """Thêm món vào giỏ hàng"""
    data = request.get_json()
    return CustomerController.add_to_cart(data, current_customer)

@customer_bp.route('/cart/update/<int:item_id>/', methods=['PUT'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Update cart item quantity'})
def update_cart_item(item_id, current_customer): 
    """Cập nhật số lượng món trong giỏ hàng"""
    data = request.get_json()
    return CustomerController.update_cart_item(item_id, data, current_customer)

@customer_bp.route('/cart/remove/<int:item_id>/', methods=['DELETE'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Remove item from cart'})
def remove_from_cart(item_id, current_customer): 
    """Xóa món khỏi giỏ hàng"""
    return CustomerController.remove_from_cart(item_id, current_customer)

@customer_bp.route('/cart/clear/', methods=['DELETE'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Clear cart'})
def clear_cart(current_customer):  
    """Xóa toàn bộ giỏ hàng"""
    return CustomerController.clear_cart(current_customer)

# Order endpoints
@customer_bp.route('/orders/', methods=['GET'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Get customer orders'})
def get_orders(current_customer): 
    """Lấy danh sách đơn hàng của khách hàng"""
    return CustomerController.get_orders(current_customer)

@customer_bp.route('/orders/<int:order_id>/', methods=['GET'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Get order details'})
def get_order(order_id, current_customer): 
    """Lấy chi tiết đơn hàng"""
    return CustomerController.get_order(order_id, current_customer)

@customer_bp.route('/orders/', methods=['POST'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Create new order'})
def create_order(current_customer): 
    """Tạo đơn hàng mới"""
    data = request.get_json()
    return CustomerController.create_order(data, current_customer)

@customer_bp.route('/orders/<int:order_id>/cancel/', methods=['PUT'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Cancel order'})
def cancel_order(order_id, current_customer):  
    """Hủy đơn hàng"""
    data = request.get_json()
    return CustomerController.cancel_order(order_id, data, current_customer)

# Review endpoints
@customer_bp.route('/reviews/<int:food_id>/', methods=['GET'])
@swag_from({'tags': ['Customer'], 'summary': 'Get food reviews'})
def get_reviews(food_id):  
    """Lấy đánh giá của món ăn"""
    return CustomerController.get_reviews_by_food(food_id)

@customer_bp.route('/restaurant/', methods=['GET'])
@swag_from({'tags': ['Customer'], 'summary': 'Get nearby restaurants'})
def get_restaurants():  
    """Lấy danh sách nhà hàng gần nhất"""
    nearby = request.args.get('nearby', 'false').lower() == 'true'
    per_page = request.args.get('per_page', type=int)
    page = request.args.get('page', 1, type=int)
    return CustomerController.get_restaurants(nearby=nearby, page=page, per_page=per_page)

@customer_bp.route('/restaurant/random/', methods=['GET'])
@swag_from({'tags': ['Customer'], 'summary': 'Get random restaurants'})
def get_random_restaurants():
    """Lấy danh sách nhà hàng ngẫu nhiên"""
    per_page = request.args.get('per_page', type=int)
    return CustomerController.get_random_restaurants(per_page=per_page)

@customer_bp.route('/reviews/', methods=['POST'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Create review'})
def create_review(current_customer): 
    """Tạo đánh giá mới"""
    data = request.get_json()
    return CustomerController.create_review(data, current_customer)

# Payment endpoints (mockup)
@customer_bp.route('/payment/deposit/', methods=['POST'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Deposit money (mockup)'})
def deposit_money(current_customer):  
    """Nạp tiền (mockup)"""
    data = request.get_json()
    return CustomerController.deposit_money(data, current_customer)

@customer_bp.route('/payment/withdraw/', methods=['POST'])
@jwt_customer_required
@swag_from({'tags': ['Customer'], 'summary': 'Withdraw money (mockup)'})
def withdraw_money(current_customer):  
    """Rút tiền (mockup)"""
    data = request.get_json()
    return CustomerController.withdraw_money(data, current_customer)
