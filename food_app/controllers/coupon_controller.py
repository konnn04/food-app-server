from food_app.dao.coupon_dao import CouponDAO
from food_app.utils.responses import success_response, error_response
from food_app.models.coupon import Coupon
from food_app.models.restaurant import Restaurant
from food_app import db

class CouponController:
    @staticmethod
    def create_coupon(data):
        try:
            if not data.get('code') or not data.get('discount_type'):
                return error_response('Thiếu thông tin bắt buộc', 400)
            coupon = CouponDAO.create_coupon(data)
            return success_response('Tạo mã giảm giá thành công', coupon.to_dict(), 201)
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def apply_coupon(code, order_amount, restaurant_id=None, food_ids=None):
        try:
            coupon = CouponDAO.get_coupon_by_code(code)
            if not coupon:
                return error_response('Mã giảm giá không hợp lệ', 404)

            if coupon.restaurant_id and restaurant_id and coupon.restaurant_id != int(restaurant_id):
                return error_response('Mã giảm giá không áp dụng cho nhà hàng này', 400)

            if coupon.start_date and coupon.start_date > __import__('datetime').datetime.utcnow():
                return error_response('Mã giảm giá chưa có hiệu lực', 400)
            if coupon.end_date and coupon.end_date < __import__('datetime').datetime.utcnow():
                return error_response('Mã giảm giá đã hết hạn', 400)

            if coupon.min_order_amount and order_amount < coupon.min_order_amount:
                return error_response('Chưa đạt giá trị tối thiểu', 400)

            discount = 0.0
            if coupon.foods and food_ids:
                # Apply only to matching food items total
                applicable = set(food_ids) & {f.id for f in coupon.foods}
                if applicable:
                    applicable_total = order_amount  # For simplicity, assume full amount
                else:
                    applicable_total = 0
            else:
                applicable_total = order_amount

            if coupon.discount_type == 'percent':
                discount = applicable_total * (coupon.discount_value / 100.0)
            else:
                discount = coupon.discount_value

            if coupon.max_discount_amount is not None:
                discount = min(discount, coupon.max_discount_amount)

            return success_response('Áp dụng mã giảm giá thành công', {
                'coupon': coupon.to_dict(),
                'discount': discount,
                'payable': max(order_amount - discount, 0)
            })
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def list_public(params):
        try:
            query = Coupon.query.filter_by(is_active=True)
            restaurant_id = params.get('restaurant_id')
            if restaurant_id:
                query = query.filter(Coupon.restaurant_id == int(restaurant_id))
            coupons = query.order_by(Coupon.id.desc()).all()
            return success_response('Lấy danh sách mã giảm giá', [c.to_dict() for c in coupons])
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_by_code(code):
        try:
            coupon = CouponDAO.get_coupon_by_code(code)
            if not coupon:
                return error_response('Không tìm thấy mã', 404)
            return success_response('OK', coupon.to_dict())
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def list_by_restaurant(restaurant_id, current_user):
        try:
            if not current_user.can_manage_restaurant(int(restaurant_id)):
                return error_response('Không có quyền', 403)
            coupons = Coupon.query.filter_by(restaurant_id=int(restaurant_id)).order_by(Coupon.id.desc()).all()
            return success_response('OK', [c.to_dict() for c in coupons])
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def staff_create(restaurant_id, data, current_user):
        try:
            restaurant_id = int(restaurant_id)
            if not current_user.can_manage_restaurant(restaurant_id):
                return error_response('Không có quyền', 403)
            data['restaurant_id'] = restaurant_id
            coupon = CouponDAO.create_coupon(data)
            return success_response('Tạo mã thành công', coupon.to_dict(), 201)
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def staff_update(coupon_id, data, current_user):
        try:
            coupon = Coupon.query.get(coupon_id)
            if not coupon:
                return error_response('Không tìm thấy mã', 404)
            if not current_user.can_manage_restaurant(coupon.restaurant_id):
                return error_response('Không có quyền', 403)
            coupon = CouponDAO.update_coupon(coupon, data)
            return success_response('Cập nhật thành công', coupon.to_dict())
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def staff_delete(coupon_id, current_user):
        try:
            coupon = Coupon.query.get(coupon_id)
            if not coupon:
                return error_response('Không tìm thấy mã', 404)
            if not current_user.can_manage_restaurant(coupon.restaurant_id):
                return error_response('Không có quyền', 403)
            db.session.delete(coupon)
            db.session.commit()
            return success_response('Đã xoá mã giảm giá')
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)


