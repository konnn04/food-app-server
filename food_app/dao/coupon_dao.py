from food_app import db
from food_app.models.coupon import Coupon
from food_app.models.food import Food

class CouponDAO:
    @staticmethod
    def create_coupon(data):
        foods = data.pop('foods', None)
        coupon = Coupon(**data)
        if foods:
            coupon.foods = Food.query.filter(Food.id.in_(foods)).all()
        db.session.add(coupon)
        db.session.commit()
        return coupon

    @staticmethod
    def get_coupon_by_code(code):
        return Coupon.query.filter_by(code=code, is_active=True).first()

    @staticmethod
    def update_coupon(coupon, data):
        foods = data.pop('foods', None)
        for k, v in data.items():
            setattr(coupon, k, v)
        if foods is not None:
            coupon.foods = Food.query.filter(Food.id.in_(foods)).all()
        db.session.commit()
        return coupon


