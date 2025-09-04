from food_app import db
from datetime import datetime

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # Giá tại thời điểm đặt hàng
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', back_populates='items')
    food = db.relationship('Food', back_populates='order_items')
    toppings = db.relationship('OrderItemTopping', back_populates='order_item', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'food_image': self.food.image_url if self.food else None,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.price * self.quantity,
            'toppings': [topping.to_dict() for topping in self.toppings],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
