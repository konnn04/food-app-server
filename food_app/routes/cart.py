from flask import Blueprint, request
from food_app.controllers.cart_controller import CartController
from flasgger import swag_from

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/', methods=['GET'])
@swag_from({'tags': ['Cart'], 'summary': 'Get cart by customer'})
def get_cart():
    customer_id = request.args.get('customer_id')
    return CartController.get_cart(customer_id)

@cart_bp.route('/add/', methods=['POST'])
@swag_from({'tags': ['Cart'], 'summary': 'Add item to cart'})
def add_to_cart():
    data = request.get_json()
    return CartController.add_to_cart(data)

@cart_bp.route('/clear/', methods=['POST'])
@swag_from({'tags': ['Cart'], 'summary': 'Clear cart'})
def clear_cart():
    data = request.get_json()
    customer_id = data.get('customer_id')
    return CartController.clear_cart(customer_id)


