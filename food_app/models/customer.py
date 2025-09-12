from food_app import db
from datetime import datetime
from .base_user import BaseUser

class Customer(BaseUser):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, db.ForeignKey('base_users.id'), primary_key=True)

    loyalty_points = db.Column(db.Integer, default=0)
    total_orders = db.Column(db.Integer, default=0)
    firebase_uid = db.Column(db.String(100), unique=True, nullable=True)

    orders = db.relationship('Order', back_populates='customer', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }

    def to_dict(self):
        return self.base_to_dict()
