from food_app.dao.cart_dao import CartDAO
from food_app.utils.responses import success_response, error_response

class CartController:
    @staticmethod
    def add_to_cart(data):
        try:
            customer_id = data.get('customer_id')
            food_id = data.get('food_id')
            if not customer_id or not food_id:
                return error_response('Thiếu thông tin', 400)
            restaurant_id = data.get('restaurant_id')
            cart = CartDAO.get_or_create_cart(customer_id, restaurant_id)
            item = CartDAO.add_item(cart, food_id, data.get('quantity', 1), data.get('price'), data.get('toppings'))
            return success_response('Đã thêm vào giỏ hàng', item.to_dict(), 201)
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_cart(customer_id):
        try:
            cart = CartDAO.get_or_create_cart(customer_id)
            return success_response('Lấy giỏ hàng thành công', {
                'id': cart.id,
                'customer_id': cart.customer_id,
                'restaurant_id': cart.restaurant_id,
                'items': [i.to_dict() for i in cart.items]
            })
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def clear_cart(customer_id):
        try:
            cart = CartDAO.get_or_create_cart(customer_id)
            CartDAO.clear_cart(cart)
            return success_response('Đã xóa giỏ hàng')
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)


