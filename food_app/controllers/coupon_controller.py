from food_app.dao.coupon_dao import CouponDAO
from food_app.utils.responses import success_response, error_response

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


