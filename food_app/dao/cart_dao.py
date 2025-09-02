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
        elif restaurant_id and cart.restaurant_id != restaurant_id:
            cart.restaurant_id = restaurant_id
            db.session.commit()
        return cart

    @staticmethod
    def add_item(cart, food_id, quantity=1, price=None, toppings=None):
        food = Food.query.get(food_id)
        if not food:
            raise ValueError('Món ăn không tồn tại')
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
    def clear_cart(cart):
        for item in list(cart.items):
            db.session.delete(item)
        db.session.commit()
        return True


