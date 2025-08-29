from food_app import db
from datetime import datetime

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    opening_hours = db.Column(db.JSON)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_restaurants')
    users = db.relationship('User', foreign_keys='User.restaurant_id', back_populates='restaurant')
    foods = db.relationship('Food', back_populates='restaurant', lazy=True)
    orders = db.relationship('Order', back_populates='restaurant', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'description': self.description,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'opening_hours': self.opening_hours,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }