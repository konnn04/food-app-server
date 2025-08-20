from app import db
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
    opening_hours = db.Column(db.JSON)  # {"mon": "8:00-22:00", "tue": "8:00-22:00", ...}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - remove the backref since it's defined in Food model
    # foods relationship will be created automatically by the backref in Food model
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None
        }