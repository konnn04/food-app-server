from food_app import db
from food_app.models.user import User
from food_app.models.customer import Customer
from food_app.models.restaurant import Restaurant
from food_app.models.food import Food
from food_app.models.order import Order, OrderItem
from food_app.models.category import Category
from food_app.models.otp import OTP
from datetime import datetime, time
from sqlalchemy import func

class UserDAO:
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_phone(phone):
        return User.query.filter_by(phone=phone).first()

    @staticmethod
    def get_user_by_credentials(credential):
        """Tìm user theo username, email hoặc phone"""
        return User.query.filter(
            (User.username == credential) |
            (User.email == credential) |
            (User.phone == credential)
        ).first()

    @staticmethod
    def get_users_by_role(role=None):
        if role:
            return User.query.filter_by(role=role).all()
        return User.query.all()

    @staticmethod
    def create_user(user_data):
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user, update_data):
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return user

    @staticmethod
    def update_last_login(user):
        user.last_login = datetime.utcnow()
        db.session.commit()

class CustomerDAO:
    @staticmethod
    def get_customer_by_id(customer_id):
        return Customer.query.get(customer_id)

    @staticmethod
    def get_customer_by_phone(phone):
        return Customer.query.filter_by(phone=phone).first()

    @staticmethod
    def get_all_customers():
        return Customer.query.all()

    @staticmethod
    def create_customer(customer_data):
        customer = Customer(**customer_data)
        db.session.add(customer)
        db.session.commit()
        return customer

    @staticmethod
    def update_customer(customer, update_data):
        for key, value in update_data.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        db.session.commit()
        return customer

    @staticmethod
    def get_new_customers_today():
        today = datetime.now().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)
        return Customer.query.filter(Customer.created_at.between(today_start, today_end)).count()

class RestaurantDAO:
    @staticmethod
    def get_restaurant_by_id(restaurant_id):
        return Restaurant.query.get(restaurant_id)

    @staticmethod
    def get_restaurant_by_owner(owner_id):
        return Restaurant.query.filter_by(owner_id=owner_id).first()

    @staticmethod
    def get_restaurants_by_status(status):
        return Restaurant.query.filter_by(approval_status=status).all()

    @staticmethod
    def create_restaurant(restaurant_data):
        restaurant = Restaurant(**restaurant_data)
        db.session.add(restaurant)
        db.session.commit()
        return restaurant

    @staticmethod
    def update_restaurant(restaurant, update_data):
        for key, value in update_data.items():
            setattr(restaurant, key, value)
        db.session.commit()
        return restaurant

class FoodDAO:
    @staticmethod
    def get_food_by_id(food_id):
        return Food.query.get(food_id)

    @staticmethod
    def get_foods_by_category(category=None, available_only=True):
        query = Food.query

        if category:
            query = query.filter_by(category=category)

        if available_only:
            query = query.filter_by(available=True)

        return query.all()

    @staticmethod
    def get_foods_by_restaurant(restaurant_id):
        return Food.query.filter_by(restaurant_id=restaurant_id).all()

    @staticmethod
    def create_food(food_data):
        food = Food(**food_data)
        db.session.add(food)
        db.session.commit()
        return food

    @staticmethod
    def update_food(food, update_data):
        for key, value in update_data.items():
            if hasattr(food, key):
                setattr(food, key, value)
        db.session.commit()
        return food

class OrderDAO:
    @staticmethod
    def get_order_by_id(order_id):
        return Order.query.get(order_id)

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_orders_by_restaurant(restaurant_id):
        return Order.query.filter_by(restaurant_id=restaurant_id).order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_orders_by_status(status=None):
        query = Order.query
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_all_orders():
        return Order.query.order_by(Order.created_at.desc()).all()

    @staticmethod
    def create_order(order_data, items_data):
        order = Order(**order_data)

        total_amount = 0
        restaurant_id = None

        # Thêm order items
        for item_data in items_data:
            food = FoodDAO.get_food_by_id(item_data['food_id'])
            if not food or not food.available:
                raise ValueError(f'Món ăn ID {item_data["food_id"]} không có sẵn')

            # Kiểm tra tất cả món ăn phải cùng nhà hàng
            if restaurant_id is None:
                restaurant_id = food.restaurant_id
            elif restaurant_id != food.restaurant_id:
                raise ValueError('Tất cả món ăn phải cùng một nhà hàng')

            quantity = int(item_data.get('quantity', 1))
            price = food.price

            order_item = OrderItem(
                food_id=food.id,
                quantity=quantity,
                price=price
            )
            order.order_items.append(order_item)
            total_amount += quantity * price

        order.total_amount = total_amount
        order.restaurant_id = restaurant_id

        db.session.add(order)
        db.session.commit()
        return order

    @staticmethod
    def update_order_status(order, new_status):
        order.status = new_status
        db.session.commit()
        return order

    @staticmethod
    def get_today_orders():
        today = datetime.now().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)
        return Order.query.filter(Order.created_at.between(today_start, today_end))

    @staticmethod
    def get_orders_status_counts():
        status_counts = {}
        for status in ['pending', 'confirmed', 'preparing', 'ready', 'delivering', 'delivered', 'cancelled']:
            status_counts[status] = Order.query.filter_by(status=status).count()
        return status_counts

    @staticmethod
    def get_total_revenue():
        return db.session.query(func.sum(Order.total_amount)).scalar() or 0

    @staticmethod
    def get_today_revenue():
        today_orders = OrderDAO.get_today_orders()
        return today_orders.with_entities(func.sum(Order.total_amount)).scalar() or 0

class CategoryDAO:
    @staticmethod
    def get_category_by_id(category_id):
        return Category.query.get(category_id)

    @staticmethod
    def get_all_categories():
        return Category.query.all()

    @staticmethod
    def create_category(category_data):
        category = Category(**category_data)
        db.session.add(category)
        db.session.commit()
        return category

class OTPDAO:
    @staticmethod
    def get_otp_by_phone(phone):
        return OTP.query.filter_by(phone=phone).first()

    @staticmethod
    def create_otp(otp_data):
        otp = OTP(**otp_data)
        db.session.add(otp)
        db.session.commit()
        return otp

    @staticmethod
    def delete_expired_otps():
        expired_time = datetime.utcnow() - OTP.EXPIRY_TIME
        OTP.query.filter(OTP.created_at < expired_time).delete()
        db.session.commit()

    @staticmethod
    def generate_otp_for_phone(phone):
        # Xóa OTP cũ
        OTP.query.filter_by(phone=phone).delete()

        # Tạo OTP mới
        otp_code = OTP.generate_code(phone=phone)
        otp = OTP(phone=phone, code=otp_code, expires_at=datetime.utcnow() + OTP.EXPIRY_TIME)
        db.session.add(otp)
        db.session.commit()
        return otp_code

    @staticmethod
    def verify_otp(phone, code):
        otp = OTP.query.filter_by(phone=phone, code=code).first()
        if not otp or otp.is_expired():
            return False

        # Xóa OTP sau khi sử dụng
        db.session.delete(otp)
        db.session.commit()
        return True
