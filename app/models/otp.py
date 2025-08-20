from app import db
from datetime import datetime, timedelta
import random
import string

class OTP(db.Model):
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def generate_for_phone(phone):
        """Tạo mã OTP mới cho số điện thoại"""
        # Xóa OTP cũ của số điện thoại này nếu có
        OTP.query.filter_by(phone=phone).delete()
        
        # Tạo mã OTP mới
        code = ''.join(random.choices(string.digits, k=6))
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        otp = OTP(
            phone=phone,
            code=code,
            expires_at=expires_at
        )
        
        db.session.add(otp)
        db.session.commit()
        
        return code
    
    @staticmethod
    def verify(phone, code):
        """Xác thực mã OTP"""
        otp = OTP.query.filter_by(phone=phone).first()
        
        if not otp:
            return False
        
        # Kiểm tra thời gian hết hạn
        if datetime.utcnow() > otp.expires_at:
            return False
        
        # Kiểm tra số lần thử
        if otp.attempts >= 3:
            return False
        
        # Kiểm tra mã OTP
        if otp.code != code:
            otp.attempts += 1
            db.session.commit()
            return False
        
        # OTP hợp lệ, xóa khỏi DB
        db.session.delete(otp)
        db.session.commit()
        return True
