from food_app import db
from food_app.models.cart import Cart, CartItem, CartItemTopping
from food_app.models.food import Food
from food_app.models.topping import Topping

class CartDAO:
    @staticmethod
    def get_or_create_cart(customer_id, restaurant_id=None):
        cart = Cart.query.filter_by(customer_id=customer_id).first()
        if not cart:
            cart = Cart(customer_id=customer_id, restaurant_id=restaurant_id)
            db.session.add(cart)
            db.session.commit()
        elif restaurant_id:
            # Enforce one restaurant per cart
            if cart.restaurant_id is None:
                cart.restaurant_id = restaurant_id
                db.session.commit()
            elif cart.restaurant_id != restaurant_id:
                # If cart has items, do not allow switching restaurant
                if cart.items and len(cart.items) > 0:
                    raise ValueError('Giỏ hàng chỉ được chứa món từ một nhà hàng. Vui lòng xóa giỏ hàng trước khi chọn nhà hàng khác.')
                # If empty, allow updating restaurant
                cart.restaurant_id = restaurant_id
                db.session.commit()
        return cart

    @staticmethod
    def add_item(cart, food_id, quantity=1, price=None, toppings=None):
        food = Food.query.get(food_id)
        if not food:
            raise ValueError('Món ăn không tồn tại')
        # Ensure cart restaurant consistency
        if cart.restaurant_id is None:
            cart.restaurant_id = food.restaurant_id
        elif cart.restaurant_id != food.restaurant_id:
            raise ValueError('Giỏ hàng chỉ được chứa món từ một nhà hàng. Vui lòng xóa giỏ hàng trước khi thêm món từ nhà hàng khác.')
        item = CartItem(cart_id=cart.id, food_id=food_id, quantity=quantity, price=price or food.price)
        db.session.add(item)
        db.session.flush()
        if toppings:
            for t in toppings:
                topping_id = t['topping_id'] if isinstance(t, dict) else t
                topping = Topping.query.get(topping_id)
                if not topping or not topping.is_available:
                    raise ValueError('Topping không hợp lệ')
                t_qty = int(t.get('quantity', 1)) if isinstance(t, dict) else 1
                t_price = float(t.get('price', topping.price)) if isinstance(t, dict) else topping.price
                db.session.add(CartItemTopping(cart_item_id=item.id, topping_id=topping.id, quantity=t_qty, price=t_price))
        db.session.commit()
        return item

    @staticmethod
    def get_cart_with_items_and_data(customer_id):
        """Return cart structure with nested items and toppings for a customer."""
        cart = CartDAO.get_or_create_cart(customer_id)
        items = [i.to_dict() for i in cart.items]
        return {
            'id': cart.id,
            'customer_id': cart.customer_id,
            'restaurant_id': cart.restaurant_id,
            'restaurant_name': cart.restaurant.name if cart.restaurant else None,
            'items': items
        }

    @staticmethod
    def update_item_quantity(item_id, customer_id, quantity):
        """Update quantity of a cart item that belongs to the customer's cart."""
        item = CartItem.query.join(Cart, CartItem.cart_id == Cart.id) \
            .filter(CartItem.id == item_id, Cart.customer_id == customer_id) \
            .first()
        if not item:
            return None
        item.quantity = int(quantity)
        db.session.commit()
        return item

    @staticmethod
    def remove_item(item_id, customer_id):
        """Remove a cart item that belongs to the customer's cart."""
        item = CartItem.query.join(Cart, CartItem.cart_id == Cart.id) \
            .filter(CartItem.id == item_id, Cart.customer_id == customer_id) \
            .first()
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True

    @staticmethod
    def clear_cart(customer_id):
        """Clear all items from the customer's cart."""
        cart = Cart.query.filter_by(customer_id=customer_id).first()
        if not cart:
            return True
        for item in list(cart.items):
            db.session.delete(item)
        # Reset restaurant binding after clearing
        cart.restaurant_id = None
        db.session.commit()
        return True


