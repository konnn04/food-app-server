from food_app import db
from datetime import datetime

food_toppings = db.Table(
    'food_toppings',
    db.Column('food_id', db.Integer, db.ForeignKey('foods.id'), primary_key=True),
    db.Column('topping_id', db.Integer, db.ForeignKey('toppings.id'), primary_key=True)
)

class Topping(db.Model):
    __tablename__ = 'toppings'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    foods = db.relationship('Food', secondary=food_toppings, back_populates='toppings')
    order_item_toppings = db.relationship('OrderItemTopping', back_populates='topping', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_dict_basic(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'is_available': self.is_available,
        }


