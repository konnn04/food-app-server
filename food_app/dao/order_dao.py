from food_app import db
from food_app.models.order import Order, OrderItem
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

        for item_data in items_data:
            item_data['order_id'] = order.id
            item = OrderItem(**item_data)
            db.session.add(item)

        db.session.commit()
        return order

    @staticmethod
    def update_order_status(order, new_status):
        order.status = new_status
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
