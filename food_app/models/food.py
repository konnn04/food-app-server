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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    restaurant = db.relationship('Restaurant', back_populates='foods')
    categories = db.relationship('Category', secondary='food_categories', back_populates='foods', lazy=True)
    # Toppings many-to-many
    from .topping import food_toppings
    toppings = db.relationship('Topping', secondary=food_toppings, back_populates='foods', lazy=True)
    order_items = db.relationship('OrderItem', back_populates='food', lazy=True)
    
    def to_dict(self):
        restaurant_info = None
        if self.restaurant:
            restaurant_info = {
                'id': self.restaurant.id,
                'name': self.restaurant.name,
                'address': self.restaurant.address,
                'phone': self.restaurant.phone,
                'email': self.restaurant.email,
                'description': self.restaurant.description,
                'image_url': self.restaurant.image_url,
                'opening_hours': self.restaurant.opening_hours if isinstance(self.restaurant.opening_hours, str) else str(self.restaurant.opening_hours),
                'latitude': self.restaurant.latitude,
                'longitude': self.restaurant.longitude,
                'is_active': self.restaurant.is_active,
                'approval_status': self.restaurant.approval_status,
                'tax_code': self.restaurant.tax_code
            }
        
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
            'restaurant': restaurant_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }