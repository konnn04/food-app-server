from food_app import db
from datetime import datetime

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship('Customer', backref='cart', uselist=False)
    restaurant = db.relationship('Restaurant')
    items = db.relationship('CartItem', backref='cart', cascade='all, delete-orphan')

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    food = db.relationship('Food')
    toppings = db.relationship('CartItemTopping', backref='cart_item', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'food_image': self.food.image_url if self.food else None,
            'quantity': self.quantity,
            'price': self.price,
            'toppings': [t.to_dict() for t in self.toppings],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CartItemTopping(db.Model):
    __tablename__ = 'cart_item_toppings'

    id = db.Column(db.Integer, primary_key=True)
    cart_item_id = db.Column(db.Integer, db.ForeignKey('cart_items.id'), nullable=False)
    topping_id = db.Column(db.Integer, db.ForeignKey('toppings.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    topping = db.relationship('Topping')

    def to_dict(self):
        return {
            'id': self.id,
            'topping_id': self.topping_id,
            'topping_name': self.topping.name if self.topping else None,
            'quantity': self.quantity,
            'price': self.price
        }


