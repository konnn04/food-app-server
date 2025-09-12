from food_app import db
from food_app.models.order import Order
from food_app.models.order_item import OrderItem
from food_app.models.order_item_topping import OrderItemTopping
from food_app.models.food import Food
from food_app.models.topping import Topping
from sqlalchemy import func

class OrderDAO:
    @staticmethod
    def get_order_by_id(order_id):
        return Order.query.get(order_id)

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.query.filter_by(customer_id=customer_id).all()

    @staticmethod
    def get_orders_by_restaurant(restaurant_id):
        return Order.query.filter_by(restaurant_id=restaurant_id).all()

    @staticmethod
    def get_orders_by_status(status=None):
        if status:
            return Order.query.filter_by(status=status).all()
        return Order.query.all()

    @staticmethod
    def get_all_orders():
        return Order.query.all()

    @staticmethod
    def create_order(order_data, items_data):
        order = Order(**order_data)
        db.session.add(order)
        db.session.flush()

        total_amount = 0.0
        for item_data in items_data:
            food = Food.query.get(item_data['food_id'])
            if not food:
                raise ValueError('Món ăn không tồn tại')
            quantity = int(item_data.get('quantity', 1))
            price = float(item_data.get('price', food.price))

            item = OrderItem(order_id=order.id, food_id=food.id, quantity=quantity, price=price)
            db.session.add(item)
            db.session.flush()

            item_total = quantity * price

            # Handle toppings - lưu từng topping riêng biệt
            toppings = item_data.get('toppings', [])
            toppings_total = 0.0
            for topping_entry in toppings:
                topping_id = topping_entry['topping_id'] if isinstance(topping_entry, dict) else topping_entry
                topping = Topping.query.get(topping_id)
                if not topping or not topping.is_available:
                    raise ValueError('Topping không hợp lệ')
                t_qty = int(topping_entry.get('quantity', 1)) if isinstance(topping_entry, dict) else 1
                t_price = float(topping_entry.get('price', topping.price)) if isinstance(topping_entry, dict) else topping.price
                
                # Tạo OrderItemTopping
                order_item_topping = OrderItemTopping(
                    order_item_id=item.id,
                    topping_id=topping.id,
                    quantity=t_qty,
                    price=t_price
                )
                db.session.add(order_item_topping)
                toppings_total += t_qty * t_price
            
            # Cập nhật giá của item để bao gồm toppings
            item.price += toppings_total
            item_total = quantity * item.price

            total_amount += item_total

        order.total_amount = total_amount
        db.session.commit()
        return order

    @staticmethod
    def update_order_status(order, new_status):
        order.status = new_status
        db.session.commit()
        return order

    @staticmethod
    def cancel_order(order, cancel_reason_id=None, cancel_note=None):
        from food_app.models.cancel_reason import CancelReason
        if order.status in ['delivered', 'cancelled']:
            raise ValueError('Đơn đã hoàn tất hoặc đã huỷ')
        if cancel_reason_id:
            reason = CancelReason.query.get(cancel_reason_id)
            if not reason:
                raise ValueError('Lý do huỷ không hợp lệ')
            order.cancel_reason_id = cancel_reason_id
        order.cancel_note = cancel_note
        order.status = 'cancelled'
        db.session.commit()
        return order

    @staticmethod
    def get_today_orders():
        today = func.current_date()
        return Order.query.filter(func.date(Order.created_at) == today).all()

    @staticmethod
    def get_orders_status_counts():
        return db.session.query(
            Order.status,
            func.count(Order.id)
        ).group_by(Order.status).all()

    @staticmethod
    def get_total_revenue():
        return db.session.query(func.sum(Order.total_amount)).scalar() or 0

    @staticmethod
    def get_today_revenue():
        today = func.current_date()
        return db.session.query(func.sum(Order.total_amount)).filter(
            func.date(Order.created_at) == today
        ).scalar() or 0
