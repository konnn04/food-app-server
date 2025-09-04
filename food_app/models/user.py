from food_app import db
from werkzeug.security import generate_password_hash, check_password_hash
from .base_user import BaseUser
from flask_login import UserMixin

class User(UserMixin, BaseUser):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, db.ForeignKey('base_users.id'), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    
    role = db.Column(db.String(20), nullable=False, default='staff') 
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=True)
    balance = db.Column(db.Float, default=0.0)  # Số dư tài khoản
    
    # Relationships
    assigned_orders = db.relationship('Order', foreign_keys='Order.assigned_staff_id', back_populates='assigned_staff')
    from .restaurant_staff import restaurant_staff
    restaurants = db.relationship('Restaurant', secondary=restaurant_staff, back_populates='staff_users')
    owned_restaurant = db.relationship('Restaurant', foreign_keys='Restaurant.owner_id', back_populates='owner', uselist=False) 
    
    __mapper_args__ = {
        'polymorphic_identity': 'staff'
    }
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
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
            'balance': self.balance,
            'restaurants': [{'id': r.id, 'name': r.name} for r in self.restaurants],
            'owned_restaurant': self.owned_restaurant.to_dict() if self.owned_restaurant else None
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
        if self.role == 'owner':
            # Owner chỉ quản lý restaurant của mình
            return self.owned_restaurant and self.owned_restaurant.id == restaurant_id
        if self.role in ['manager', 'staff']:
            return any(r.id == restaurant_id for r in self.restaurants)
        return False
    
    def can_invite_staff(self):
        """Kiểm tra có quyền mời staff không"""
        return self.role in ['owner', 'manager']
    