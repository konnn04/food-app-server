from food_app import db
from datetime import datetime

coupon_foods = db.Table(
    'coupon_foods',
    db.Column('coupon_id', db.Integer, db.ForeignKey('coupons.id'), primary_key=True),
    db.Column('food_id', db.Integer, db.ForeignKey('foods.id'), primary_key=True)
)

class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    discount_type = db.Column(db.String(20), nullable=False)  # percent | amount
    discount_value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    min_order_amount = db.Column(db.Float, nullable=True)
    max_discount_amount = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    restaurant = db.relationship('Restaurant')
    foods = db.relationship('Food', secondary=coupon_foods, backref='coupons')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'min_order_amount': self.min_order_amount,
            'max_discount_amount': self.max_discount_amount,
            'is_active': self.is_active,
            'restaurant_id': self.restaurant_id,
            'foods': [f.id for f in self.foods]
        }


