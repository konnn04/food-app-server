from food_app import db
from datetime import datetime
import random

class BaseUser(db.Model):
    __tablename__ = 'base_users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    avatar = db.Column(db.String(255), nullable=True, default=f'https://api.dicebear.com/7.x/micah/png?seed={random.randint(1, 1000)}')
    phone = db.Column(db.String(20), unique=True, nullable=True)
    gender = db.Column(db.String(10), nullable=False, default='male') 
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Discriminator column for inheritance
    user_type = db.Column(db.String(20), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'base_user',
        'polymorphic_on': user_type
    }
    
    def base_to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'full_name': self.first_name + ' ' + self.last_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'avatar': self.avatar,
            'gender': self.gender, 
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'address': self.address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'user_type': self.user_type
        }
