from food_app import db
from datetime import datetime

class Invitation(db.Model):
    __tablename__ = 'invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    invited_username = db.Column(db.String(80), nullable=False)  # Username của người được mời
    invited_email = db.Column(db.String(120), nullable=True)    # Email của người được mời
    role = db.Column(db.String(20), nullable=False)  # 'staff' hoặc 'manager'
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, expired
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Owner mời
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)
    message = db.Column(db.Text, nullable=True)  # Thông điệp từ owner
    
    # Relationships
    restaurant = db.relationship('Restaurant', backref='invitations')
    inviter = db.relationship('User', foreign_keys=[invited_by], backref='sent_invitations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else None,
            'invited_username': self.invited_username,
            'invited_email': self.invited_email,
            'role': self.role,
            'status': self.status,
            'invited_by': self.invited_by,
            'inviter_name': self.inviter.full_name if self.inviter else None,
            'invited_at': self.invited_at.isoformat() if self.invited_at else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'message': self.message
        }
    
    def accept(self, user):
        """Chấp nhận lời mời"""
        from datetime import datetime
        self.status = 'accepted'
        self.responded_at = datetime.utcnow()
        # Gán user vào restaurant
        user.restaurant_id = self.restaurant_id
        user.role = self.role
    
    def reject(self):
        """Từ chối lời mời"""
        from datetime import datetime
        self.status = 'rejected'
        self.responded_at = datetime.utcnow()
    
    def expire(self):
        """Hết hạn lời mời"""
        self.status = 'expired'