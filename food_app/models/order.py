from food_app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    cancel_reason_id = db.Column(db.Integer, db.ForeignKey('cancel_reasons.id'), nullable=True)
    cancel_note = db.Column(db.Text, nullable=True)
    delivery_address = db.Column(db.Text)
    delivery_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancel_reason = db.relationship('CancelReason')
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    restaurant = db.relationship('Restaurant', back_populates='orders')
    customer = db.relationship('Customer', back_populates='orders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,  # SỬA
            'customer_phone': self.customer.phone if self.customer else None,     # SỬA
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else None,
            'total_amount': self.total_amount,
            'status': self.status,
            'cancel_reason_id': self.cancel_reason_id,
            'cancel_reason': self.cancel_reason.description if self.cancel_reason else None,
            'cancel_note': self.cancel_note,
            'delivery_address': self.delivery_address,
            'delivery_phone': self.delivery_phone,
            'notes': self.notes,
            'assigned_staff_id': self.assigned_staff_id,
            'assigned_staff_name': self.assigned_staff.full_name if self.assigned_staff else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.order_items]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    # Relationship
    food = db.relationship('Food', backref='food_order_items')
    from .topping import Topping
    item_toppings = db.relationship('OrderItemTopping', backref='order_item', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'quantity': self.quantity,
            'price': self.price,
            'toppings': [it.to_dict() for it in self.item_toppings],
            'subtotal': self.quantity * self.price + sum(it.quantity * it.price for it in self.item_toppings)
        }

class OrderItemTopping(db.Model):
    __tablename__ = 'order_item_toppings'

    id = db.Column(db.Integer, primary_key=True)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False)
    topping_id = db.Column(db.Integer, db.ForeignKey('toppings.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False, default=0.0)

    topping = db.relationship('Topping')

    def to_dict(self):
        return {
            'id': self.id,
            'topping_id': self.topping_id,
            'topping_name': self.topping.name if self.topping else None,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.quantity * self.price
        }