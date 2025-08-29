from food_app import db
from werkzeug.security import generate_password_hash, check_password_hash
from .base_user import BaseUser

class User(BaseUser):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, db.ForeignKey('base_users.id'), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    role = db.Column(db.String(20), nullable=False, default='staff') 
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=True)
    
    # Relationships
    assigned_orders = db.relationship('Order', foreign_keys='Order.assigned_staff_id', backref='assigned_staff')
    restaurant = db.relationship('Restaurant', foreign_keys=[restaurant_id], back_populates='users')

    __mapper_args__ = {
        'polymorphic_identity': 'staff'
    }
    
    def has_role(self, role):
        """Kiểm tra quyền"""
        role_hierarchy = {
            'staff': 1,
            'manager': 2,
            'owner': 3,
            'admin': 4
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(role, 0)
    
    def to_dict(self):
        data = self.base_to_dict()
        data.update({
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else None
        })
        return data
    
    def set_password(self, password):
        """Đặt mật khẩu"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Kiểm tra mật khẩu"""
        return check_password_hash(self.password_hash, password)
    
    def can_manage_restaurant(self, restaurant_id):
        """Kiểm tra quyền quản lý restaurant"""
        if self.role == 'admin':
            return True
        if self.role in ['manager', 'owner']:
            # Owner có thể quản lý restaurant của mình
            # Manager có thể quản lý restaurant được gán
            return self.restaurant_id == restaurant_id or \
                   any(r.id == restaurant_id for r in self.owned_restaurants)
        return False