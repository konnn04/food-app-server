from food_app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_phone = db.Column(db.String(20), nullable=False)
    delivery_note = db.Column(db.Text, nullable=True)
    cancel_reason = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    items = db.relationship('OrderItem', back_populates='order', lazy=True, cascade='all, delete-orphan')
    restaurant = db.relationship('Restaurant', back_populates='orders')
    customer = db.relationship('Customer', foreign_keys=[customer_id])
    assigned_staff = db.relationship('User', foreign_keys=[assigned_staff_id], back_populates='assigned_orders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': (self.customer.first_name + ' ' + self.customer.last_name) if self.customer else None,
            'customer_phone': self.customer.phone if self.customer else None,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else None,
            'total_amount': self.total_amount,
            'status': self.status,
            'delivery_address': self.delivery_address,
            'delivery_phone': self.delivery_phone,
            'delivery_note': self.delivery_note,
            'cancel_reason': self.cancel_reason,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'items': [item.to_dict() for item in self.items]
        }

