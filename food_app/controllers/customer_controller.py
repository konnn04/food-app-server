from flask import request
from food_app.dao.customer_dao import CustomerDAO
from food_app.dao.cart_dao import CartDAO
from food_app.dao.food_dao import FoodDAO
from food_app.dao.order_dao import OrderDAO
from food_app.dao.review_dao import ReviewDAO
from food_app.utils.responses import success_response, error_response
from food_app.utils.pagination import paginate
from food_app.utils.validators import validate_order_data
from datetime import datetime
from food_app.models.food import Food
from food_app.models.order import Order
from food_app.models.review import Review
from food_app.models.order_item import OrderItem
from food_app.models.cart import Cart
from food_app.models.customer import Customer
from sqlalchemy import and_, or_

class CustomerController:
    @staticmethod
    def get_profile(current_customer=None):
        """Lấy thông tin cá nhân"""
        try:
            # Nếu current_customer được truyền từ decorator
            if current_customer:
                return success_response(
                    message="Lấy thông tin cá nhân thành công",
                    data=current_customer.to_dict()
                )
            
            # Không có current_customer thì coi như không xác thực đúng cách
            return error_response("Không tìm thấy khách hàng")
        except Exception as e:
            return error_response(f"Lỗi lấy thông tin cá nhân: {str(e)}")

    @staticmethod
    def update_profile(data, current_customer):
        """Cập nhật thông tin cá nhân"""
        try:
            update_data = {}
            fields = ['full_name', 'phone', 'email', 'address']
            
            for field in fields:
                if field in data:
                    update_data[field] = data[field]
            
            CustomerDAO.update_customer(current_customer, update_data)
            return success_response("Cập nhật thông tin thành công")
        except Exception as e:
            return error_response(f"Lỗi cập nhật thông tin: {str(e)}")

    @staticmethod
    def get_cart(current_customer):  # Nhận customer từ decorator
        """Lấy giỏ hàng của khách hàng"""
        try:
            cart_data = CartDAO.get_cart_with_items_and_data(current_customer.id)
            return success_response("Lấy giỏ hàng thành công", cart_data)
        except Exception as e:
            return error_response(f"Lỗi lấy giỏ hàng: {str(e)}")

    @staticmethod
    def add_to_cart(data, current_customer):
        """Thêm món vào giỏ hàng"""
        try:
            food_id = data.get('food_id')
            quantity = data.get('quantity', 1)
            topping_ids = data.get('topping_ids', [])
            
            if not food_id:
                return error_response("Thiếu food_id")
            
            # Kiểm tra món ăn có tồn tại và available không
            food = FoodDAO.get_food_by_id(food_id)
            if not food:
                return error_response("Món ăn không tồn tại")
            
            if not food.available:
                return error_response("Món ăn hiện không khả dụng")
            
            # Kiểm tra nhà hàng có mở cửa không
            if not food.restaurant.is_active:
                return error_response("Nhà hàng hiện không hoạt động")
            
            # Lấy hoặc tạo cart cho customer
            cart = CartDAO.get_or_create_cart(current_customer.id, food.restaurant_id)
            
            # Tạo danh sách toppings theo định dạng yêu cầu
            toppings = []
            if topping_ids:
                for topping_id in topping_ids:
                    toppings.append({'topping_id': topping_id})
        
            # Thêm item vào cart
            CartDAO.add_item(cart, food_id, quantity, food.price, toppings)
            
            return success_response("Thêm vào giỏ hàng thành công")
        
        except ValueError as e:
            return error_response(str(e))
        except Exception as e:
            return error_response(f"Lỗi thêm vào giỏ hàng: {str(e)}")

    @staticmethod
    def update_cart_item(item_id, data, current_customer):
        """Cập nhật số lượng món trong giỏ hàng"""
        try:
            quantity = data.get('quantity')
            
            if quantity is None or quantity < 1:
                return error_response("Số lượng không hợp lệ")
            
            updated_item = CartDAO.update_item_quantity(item_id, current_customer.id, quantity)
            
            if not updated_item:
                return error_response("Không tìm thấy món trong giỏ hàng")
            
            return success_response("Cập nhật giỏ hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi cập nhật giỏ hàng: {str(e)}")

    @staticmethod
    def remove_from_cart(item_id, current_customer):
        """Xóa món khỏi giỏ hàng"""
        try:
            success = CartDAO.remove_item(item_id, current_customer.id)
            
            if not success:
                return error_response("Không tìm thấy món trong giỏ hàng")
            
            return success_response("Xóa món khỏi giỏ hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi xóa món: {str(e)}")

    @staticmethod
    def clear_cart(current_customer):
        """Xóa toàn bộ giỏ hàng"""
        try:
            CartDAO.clear_cart(current_customer.id)
            return success_response("Xóa giỏ hàng thành công")
        except Exception as e:
            return error_response(f"Lỗi xóa giỏ hàng: {str(e)}")

    @staticmethod
    def get_orders(current_customer):
        """Lấy danh sách đơn hàng của khách hàng"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            query = Order.query.filter_by(customer_id=current_customer.id).order_by(Order.created_at.desc())
            orders, pagination_info = paginate(query, page, per_page)
            
            orders_data = [order.to_dict() for order in orders]
            
            return success_response(
                message="Lấy danh sách đơn hàng thành công",
                data={
                    'items': orders_data,
                    'pagination': pagination_info
                }
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy đơn hàng: {str(e)}")

    @staticmethod
    def get_order(order_id, current_customer):
        """Lấy chi tiết đơn hàng"""
        try:
            order = Order.query.filter_by(
                id=order_id, 
                customer_id=current_customer.id
            ).first()
            
            if not order:
                return error_response("Không tìm thấy đơn hàng")
            
            return success_response(
                message="Lấy chi tiết đơn hàng thành công",
                data=order.to_dict()
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy chi tiết đơn hàng: {str(e)}")

    @staticmethod
    def create_order(data, current_customer):
        """Tạo đơn hàng mới"""
        try:
            # Dữ liệu đã được truyền từ route
            
            # Validate dữ liệu
            validation_result = validate_order_data(data)
            if not validation_result['valid']:
                return error_response(validation_result['message'])
            
            # Kiểm tra giỏ hàng
            cart = CartDAO.get_or_create_cart(current_customer.id)
            cart_items = list(cart.items)
            if not cart_items:
                return error_response("Giỏ hàng trống")
            
            # Kiểm tra tất cả món ăn có available không
            order_items = []
            total_amount = 0
            restaurant_id = cart.restaurant_id
            
            for item in cart_items:
                food = Food.query.get(item.food_id)
                if not food:
                    return error_response(f"Món ăn ID {item.food_id} không tồn tại")
                
                if not food.available:
                    return error_response(f"Món ăn '{food.name}' hiện không khả dụng")
                
                if not food.restaurant.is_active:
                    return error_response(f"Nhà hàng '{food.restaurant.name}' hiện không hoạt động")
                
                # Kiểm tra giờ mở cửa
                if not food.restaurant.is_open_now():
                    return error_response(f"Nhà hàng '{food.restaurant.name}' hiện không mở cửa")
                
                # Enforce single restaurant per order from cart binding
                if restaurant_id is None:
                    restaurant_id = food.restaurant_id
                elif restaurant_id != food.restaurant_id:
                    return error_response("Không thể đặt món từ nhiều nhà hàng khác nhau")
                
                subtotal = food.price * item.quantity
                total_amount += subtotal
                
                order_items.append({
                    'food_id': item.food_id,
                    'quantity': item.quantity,
                    'price': food.price,
                    'subtotal': subtotal
                })
            
            # Áp dụng mã giảm giá an toàn phía server (nếu có)
            coupon_code = data.get('coupon_code') or data.get('code')
            discount_amount = 0.0
            if coupon_code:
                try:
                    from food_app.dao.coupon_dao import CouponDAO
                    from datetime import datetime as _dt

                    coupon = CouponDAO.get_coupon_by_code(coupon_code)
                    if not coupon:
                        return error_response("Mã giảm giá không hợp lệ")

                    # Kiểm tra hiệu lực thời gian
                    now = _dt.utcnow()
                    if coupon.start_date and coupon.start_date > now:
                        return error_response("Mã giảm giá chưa có hiệu lực")
                    if coupon.end_date and coupon.end_date < now:
                        return error_response("Mã giảm giá đã hết hạn")

                    # Kiểm tra ràng buộc nhà hàng
                    if coupon.restaurant_id and coupon.restaurant_id != int(restaurant_id):
                        return error_response("Mã giảm giá không áp dụng cho nhà hàng này")

                    # Tính tổng áp dụng theo food_ids nếu coupon giới hạn theo món
                    food_ids_in_cart = [it['food_id'] for it in order_items]
                    if getattr(coupon, 'foods', None):
                        applicable_ids = {f.id for f in coupon.foods}
                        applicable_total = 0.0
                        for it in order_items:
                            if it['food_id'] in applicable_ids:
                                applicable_total += it['subtotal']
                    else:
                        applicable_total = total_amount

                    # Kiểm tra giá trị tối thiểu
                    if coupon.min_order_amount and applicable_total < float(coupon.min_order_amount):
                        return error_response("Chưa đạt giá trị tối thiểu để áp dụng mã")

                    # Tính discount
                    if coupon.discount_type == 'percent':
                        discount_amount = applicable_total * (float(coupon.discount_value) / 100.0)
                    else:
                        discount_amount = float(coupon.discount_value or 0)

                    # Giới hạn mức giảm tối đa
                    if coupon.max_discount_amount is not None:
                        try:
                            discount_amount = min(discount_amount, float(coupon.max_discount_amount))
                        except Exception:
                            pass

                    # Không cho âm
                    discount_amount = max(0.0, float(discount_amount))
                    total_amount = max(0.0, float(total_amount) - discount_amount)
                except ValueError as e:
                    return error_response(str(e))
                except Exception as e:
                    return error_response(f"Lỗi áp mã giảm giá: {str(e)}")

            # Tạo đơn hàng
            delivery_note = data.get('delivery_note', data.get('note', ''))

            new_order = Order(
                customer_id=current_customer.id,
                restaurant_id=restaurant_id,
                delivery_address=data['delivery_address'],
                delivery_phone=data['delivery_phone'],
                delivery_note=delivery_note,
                total_amount=total_amount,
                status='pending'
            )
            
            Order.query.session.add(new_order)
            Order.query.session.flush()  # Để lấy ID của order
            
            # Tạo order items
            for item in order_items:
                from food_app.models.order_item import OrderItem
                order_item = OrderItem(
                    order_id=new_order.id,
                    food_id=item['food_id'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                Order.query.session.add(order_item)
            
            # Xóa các item trong giỏ (giữ cart để tránh lỗi FK)
            CartDAO.clear_cart(current_customer.id)
            
            Order.query.session.commit()
            
            result = new_order.to_dict()
            if coupon_code:
                result['coupon_applied'] = {
                    'code': coupon_code,
                    'discount_amount': float(discount_amount)
                }

            return success_response(
                message="Tạo đơn hàng thành công",
                data=result
            )
            
        except Exception as e:
            return error_response(f"Lỗi tạo đơn hàng: {str(e)}")

    @staticmethod
    def cancel_order(order_id, data, current_customer):
        """Hủy đơn hàng"""
        try:
            reason = data.get('reason', '')
            
            order = Order.query.filter_by(
                id=order_id, 
                customer_id=current_customer.id
            ).first()
            
            if not order:
                return error_response("Không tìm thấy đơn hàng")
            
            if order.status not in ['pending', 'accepted']:
                return error_response("Không thể hủy đơn hàng ở trạng thái này")
            
            order.status = 'cancelled'
            order.cancel_reason = reason
            order.cancelled_at = datetime.utcnow()
            
            Order.query.session.commit()
            
            return success_response("Hủy đơn hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi hủy đơn hàng: {str(e)}")

    @staticmethod
    def get_reviews(restaurant_id):
        """Lấy đánh giá của nhà hàng"""
        try:
            page = request.args.get('page', type=int)
            per_page = request.args.get('per_page', type=int)
            
            query = Review.query
            if restaurant_id:
                query = query.filter_by(restaurant_id=restaurant_id)
            
            query = query.order_by(Review.created_at.desc())
            reviews, pagination_info = paginate(query, page, per_page)
            
            reviews_data = [review.to_dict() for review in reviews]
            
            return success_response(
                message="Lấy đánh giá thành công",
                data={
                    'items': reviews_data,
                    'pagination': pagination_info
                }
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy đánh giá: {str(e)}")

    @staticmethod
    def create_review(data, current_customer):
        """Tạo đánh giá mới cho món ăn"""
        try:
            food_id = data.get('food_id')
            rating = data.get('rating')
            comment = data.get('comment', '')
            
            if not food_id or not rating:
                return error_response("Thiếu thông tin đánh giá")
            
            if not (1 <= rating <= 5):
                return error_response("Đánh giá phải từ 1-5")
            
            # Kiểm tra món ăn có tồn tại không
            food = Food.query.get(food_id)
            if not food:
                return error_response("Món ăn không tồn tại")
            
            # Kiểm tra đã mua món ăn này chưa
            has_ordered = OrderItem.query.join(Order).filter(
                OrderItem.food_id == food_id,
                Order.customer_id == current_customer.id,
                Order.status.in_(['completed', 'accepted'])
            ).first()
            
            if not has_ordered:
                return error_response("Bạn chưa mua món ăn này, không thể đánh giá")
            
            # Kiểm tra đã đánh giá món ăn này chưa
            existing_review = Review.query.filter_by(
                customer_id=current_customer.id,
                food_id=food_id
            ).first()
            
            if existing_review:
                return error_response("Bạn đã đánh giá món ăn này rồi")
            
            new_review = Review(
                customer_id=current_customer.id,
                food_id=food_id,
                restaurant_id=food.restaurant_id,
                rating=rating,
                comment=comment
            )
            
            Review.query.session.add(new_review)
            Review.query.session.commit()
            
            return success_response("Tạo đánh giá thành công")
            
        except Exception as e:
            return error_response(f"Lỗi tạo đánh giá: {str(e)}")

    @staticmethod
    def deposit_money(data, current_customer):
        """Nạp tiền (mockup)"""
        try:
            amount = data.get('amount')
            if not amount or amount <= 0:
                return error_response("Số tiền không hợp lệ")
            
            # Mockup: cộng tiền vào balance
            current_customer.balance = (current_customer.balance or 0) + amount
            
            Customer.query.session.commit()
            
            return success_response(
                message="Nạp tiền thành công",
                data={'new_balance': current_customer.balance}
            )
            
        except Exception as e:
            return error_response(f"Lỗi nạp tiền: {str(e)}")

    @staticmethod
    def withdraw_money(data, current_customer):
        """Rút tiền (mockup)"""
        try:
            amount = data.get('amount')
            if not amount or amount <= 0:
                return error_response("Số tiền không hợp lệ")
            
            if (current_customer.balance or 0) < amount:
                return error_response("Số dư không đủ")
            
            # Mockup: trừ tiền khỏi balance
            current_customer.balance -= amount
            
            Customer.query.session.commit()
            
            return success_response(
                message="Rút tiền thành công",
                data={'new_balance': current_customer.balance}
            )
            
        except Exception as e:
            return error_response(f"Lỗi rút tiền: {str(e)}")
