from food_app import db
from food_app.models.otp import OTP
from datetime import datetime, timedelta
import random

class OTPDAO:
    @staticmethod
    def get_otp_by_phone(phone):
        return OTP.query.filter_by(phone=phone).first()

    @staticmethod
    def create_otp(otp_data):
        otp = OTP(**otp_data)
        db.session.add(otp)
        db.session.commit()
        return otp

    @staticmethod
    def delete_expired_otps():
        expired_time = datetime.utcnow() - timedelta(minutes=5)
        OTP.query.filter(OTP.created_at < expired_time).delete()
        db.session.commit()

    @staticmethod
    def generate_otp_for_phone(phone):
        OTPDAO.delete_expired_otps()

        otp_code = str(random.randint(100000, 999999))

        otp_data = {
            'phone': phone,
            'code': otp_code,
            'expires_at': datetime.utcnow() + timedelta(minutes=5)
        }

        existing_otp = OTPDAO.get_otp_by_phone(phone)
        if existing_otp:
            existing_otp.code = otp_code
            existing_otp.expires_at = otp_data['expires_at']
            db.session.commit()
            return otp_code

        OTPDAO.create_otp(otp_data)
        return otp_code

    @staticmethod
    def verify_otp(phone, code):
        otp = OTPDAO.get_otp_by_phone(phone)
        if not otp:
            return False

        if otp.code != code or otp.expires_at < datetime.utcnow():
            return False

        db.session.delete(otp)
        db.session.commit()
        return True
