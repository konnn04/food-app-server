from food_app import db
from datetime import datetime

# Bảng liên kết nhân viên với nhiều nhà hàng
restaurant_staff = db.Table(
    'restaurant_staff',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurants.id'), primary_key=True),
    db.Column('role', db.String(20), nullable=False, default='staff'),
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)


