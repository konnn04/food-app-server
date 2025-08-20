from app import db
from datetime import datetime
from .base_user import BaseUser

class Customer(BaseUser):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, db.ForeignKey('base_users.id'), primary_key=True)
    
    # Customer specific fields - removed Firebase fields
    email = db.Column(db.String(120), unique=True, nullable=True)
    loyalty_points = db.Column(db.Integer, default=0)
    total_orders = db.Column(db.Integer, default=0)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }
    
    def to_dict(self):
        data = self.base_to_dict()
        data.update({
            'email': self.email,
            'loyalty_points': self.loyalty_points,
            'total_orders': self.total_orders,
            'role': 'customer'
        })
        return data
