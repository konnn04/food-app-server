from food_app import db
from food_app.models.customer import Customer
from food_app.models.base_user import BaseUser
from food_app.utils.validators import normalize_phone
from datetime import datetime

class CustomerDAO:
    @staticmethod
    def get_customer_by_id(customer_id):
        return Customer.query.get(customer_id)

    @staticmethod
    def get_customer_by_phone(phone):
        normalized_phone = normalize_phone(phone)
        base_user = BaseUser.query.filter_by(phone=normalized_phone, user_type='customer').first()
        if base_user:
            return Customer.query.get(base_user.id)
        return None

    @staticmethod
    def get_all_customers():
        return Customer.query.all()

    @staticmethod
    def create_customer(customer_data):
        from food_app.models.customer import Customer
        
        phone = customer_data.get('phone')
        if not phone:
            raise ValueError("Phone is required")
        
        normalized_phone = normalize_phone(phone)
        existing_base = BaseUser.query.filter_by(phone=normalized_phone).first()
        
        if existing_base:
            if existing_base.user_type == 'customer':
                return Customer.query.get(existing_base.id)
            else:
                raise ValueError(f"Số điện thoại đã được đăng ký bởi tài khoản khác")
        
        customer = Customer(
            first_name=customer_data.get('first_name', 'Khách hàng'),
            last_name=customer_data.get('last_name', 'Mới'),
            phone=normalized_phone,
            gender=customer_data.get('gender', 'male'),
            address=customer_data.get('address', ''),
            user_type='customer',
            is_need_update=True
        )
        
        db.session.add(customer)
        db.session.commit()
        return customer

    @staticmethod
    def update_customer(customer, update_data):
        for key, value in update_data.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
            elif hasattr(customer, key):
                setattr(customer, key, value)

        if update_data:
            customer.is_need_update = False

        db.session.commit()
        return customer

    @staticmethod
    def get_new_customers_today():
        today = datetime.utcnow().date()
        return Customer.query.filter(
            db.func.date(Customer.created_at) == today
        ).count()
