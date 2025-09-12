from food_app import db
from datetime import datetime

class OrderItemTopping(db.Model):
    __tablename__ = 'order_item_toppings'

    id = db.Column(db.Integer, primary_key=True)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False)
    topping_id = db.Column(db.Integer, db.ForeignKey('toppings.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order_item = db.relationship('OrderItem', back_populates='toppings')
    topping = db.relationship('Topping', back_populates='order_item_toppings')

    def to_dict(self):
        return {
            'id': self.id,
            'order_item_id': self.order_item_id,
            'topping_id': self.topping_id,
            'topping_name': self.topping.name if self.topping else None,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.price * self.quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
