from food_app import db
from datetime import datetime

class Food(db.Model):
    __tablename__ = 'foods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    available = db.Column(db.Boolean, default=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)  # THÊM
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    restaurant = db.relationship('Restaurant', back_populates='foods')
    categories = db.relationship('Category', secondary='food_categories', back_populates='foods', lazy=True)
    # Toppings many-to-many
    from .topping import food_toppings
    toppings = db.relationship('Topping', secondary=food_toppings, back_populates='foods', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'categories': [category.name for category in self.categories],
            'toppings': [t.to_dict_basic() for t in self.toppings],
            'image_url': self.image_url,
            'available': self.available,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }