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
    # Geo coordinates
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Mối quan hệ 1-1 với owner
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)  
    
    tax_code = db.Column(db.String(20), unique=True, nullable=True)  
    approval_status = db.Column(db.String(20), default='pending')  
    approval_date = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], back_populates='owned_restaurant') 
    from .restaurant_staff import restaurant_staff
    staff_users = db.relationship('User', secondary=restaurant_staff, back_populates='restaurants')  
    foods = db.relationship('Food', back_populates='restaurant', lazy=True)
    orders = db.relationship('Order', back_populates='restaurant', lazy=True)

    def to_dict(self, include_sensitive=False):
        """Convert to dict, optionally including sensitive information"""
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'description': self.description,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'opening_hours': self.opening_hours,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                'tax_code': self.tax_code,
                'approval_status': self.approval_status,
                'approval_date': self.approval_date.isoformat() if self.approval_date else None,
                'rejection_reason': self.rejection_reason,
                'owner_id': self.owner_id,
                'owner_name': self.owner.full_name if self.owner else None
            })
        
        return data
    
    def can_be_approved(self):
        """Kiểm tra restaurant có đủ điều kiện phê duyệt không"""
        return (
            self.name and
            self.address and
            self.phone and
            self.email and
            self.tax_code and
            self.approval_status == 'pending'
        )
    
    def approve(self, approved_by=None):
        """Phê duyệt restaurant"""
        from datetime import datetime
        self.approval_status = 'approved'
        self.approval_date = datetime.utcnow()
        self.rejection_reason = None
    
    def reject(self, reason, rejected_by=None):
        """Từ chối phê duyệt restaurant"""
        from datetime import datetime
        self.approval_status = 'rejected'
        self.approval_date = datetime.utcnow()
        self.rejection_reason = reason
    
    def get_staff_count(self):
        """Đếm số lượng staff/manager"""
        return len([user for user in self.staff_users if user.role in ['staff', 'manager']])
    
    def is_open_now(self):
        """Kiểm tra nhà hàng có đang mở cửa không"""
        if not self.opening_hours:
            return True  # Nếu không có giờ mở cửa thì mặc định mở
        
        from datetime import datetime
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        current_day = now.strftime('%A').lower()
        
        # Chuyển đổi tên ngày sang tiếng Việt
        day_mapping = {
            'monday': 'thứ 2',
            'tuesday': 'thứ 3', 
            'wednesday': 'thứ 4',
            'thursday': 'thứ 5',
            'friday': 'thứ 6',
            'saturday': 'thứ 7',
            'sunday': 'chủ nhật'
        }
        
        current_day_vn = day_mapping.get(current_day, current_day)
        
        # Kiểm tra trong opening_hours
        if isinstance(self.opening_hours, dict):
            day_schedule = self.opening_hours.get(current_day_vn)
            if day_schedule:
                if isinstance(day_schedule, str):
                    # Format: "08:00-22:00"
                    if '-' in day_schedule:
                        start_time, end_time = day_schedule.split('-')
                        return start_time <= current_time <= end_time
                elif isinstance(day_schedule, dict):
                    # Format: {"open": "08:00", "close": "22:00"}
                    open_time = day_schedule.get('open', '00:00')
                    close_time = day_schedule.get('close', '23:59')
                    return open_time <= current_time <= close_time
        
        return True  # Mặc định mở nếu không có thông tin
    
    # Invitation feature removed