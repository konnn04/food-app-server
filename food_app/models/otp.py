from food_app import db
from datetime import datetime, timedelta
import random
import string

class OTP(db.Model):
    __tablename__ = 'otps'
    
    EXPIRY_TIME = timedelta(minutes=5) 
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + OTP.EXPIRY_TIME)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def generate_code(phone):
        OTP.query.filter_by(phone=phone).delete()
        
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
        otp = OTP.query.filter_by(phone=phone).first()
        
        if not otp:
            return False
        
        if datetime.utcnow() > otp.expires_at:
            return False
        
        if otp.attempts >= 3:
            return False
        
        if otp.code != code:
            otp.attempts += 1
            db.session.commit()
            return False
        
        db.session.delete(otp)
        db.session.commit()
        return True
