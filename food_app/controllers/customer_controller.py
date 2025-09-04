from flask import request
from flask_jwt_extended import get_jwt_identity
from food_app.models.customer import Customer
from food_app.models.cart import Cart
from food_app.models.food import Food
from food_app.models.order import Order
from food_app.models.order_item import OrderItem
from food_app.models.review import Review
from food_app.models.restaurant import Restaurant
from food_app.utils.responses import success_response, error_response
from food_app.utils.pagination import paginate
from food_app.utils.validators import validate_order_data
from datetime import datetime
from sqlalchemy import and_, or_

class CustomerController:
    @staticmethod
    def get_cart():
        """Lấy giỏ hàng của khách hàng"""
        try:
            user_id = get_jwt_identity()
            customer = Customer.query.get(user_id)
            if not customer:
                return error_response("Không tìm thấy khách hàng")
            
            cart_items = Cart.query.filter_by(customer_id=user_id).all()
            cart_data = []
            total_amount = 0
            
            for item in cart_items:
                food = Food.query.get(item.food_id)
                if food and food.available:
                    item_data = {
                        'id': item.id,
                        'food_id': item.food_id,
                        'food_name': food.name,
                        'food_price': food.price,
                        'food_image': food.image_url,
                        'quantity': item.quantity,
                        'subtotal': food.price * item.quantity,
                        'restaurant_id': food.restaurant_id,
                        'restaurant_name': food.restaurant.name if food.restaurant else None
                    }
                    cart_data.append(item_data)
                    total_amount += item_data['subtotal']
                else:
                    # Xóa món không còn available
                    Cart.query.filter_by(id=item.id).delete()
            
            return success_response(
                message="Lấy giỏ hàng thành công",
                data={
                    'items': cart_data,
                    'total_amount': total_amount,
                    'item_count': len(cart_data)
                }
            )
        except Exception as e:
            return error_response(f"Lỗi lấy giỏ hàng: {str(e)}")

    @staticmethod
    def add_to_cart():
        """Thêm món vào giỏ hàng"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            food_id = data.get('food_id')
            quantity = data.get('quantity', 1)
            
            if not food_id:
                return error_response("Thiếu food_id")
            
            # Kiểm tra món ăn có tồn tại và available không
            food = Food.query.get(food_id)
            if not food:
                return error_response("Món ăn không tồn tại")
            
            if not food.available:
                return error_response("Món ăn hiện không khả dụng")
            
            # Kiểm tra nhà hàng có mở cửa không
            if not food.restaurant.is_active:
                return error_response("Nhà hàng hiện không hoạt động")
            
            # Kiểm tra đã có trong giỏ hàng chưa
            existing_item = Cart.query.filter_by(
                customer_id=user_id, 
                food_id=food_id
            ).first()
            
            if existing_item:
                existing_item.quantity += quantity
            else:
                new_item = Cart(
                    customer_id=user_id,
                    food_id=food_id,
                    quantity=quantity
                )
                Cart.query.session.add(new_item)
            
            Cart.query.session.commit()
            
            return success_response("Thêm vào giỏ hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi thêm vào giỏ hàng: {str(e)}")

    @staticmethod
    def update_cart_item(item_id, data):
        """Cập nhật số lượng món trong giỏ hàng"""
        try:
            user_id = get_jwt_identity()
            quantity = data.get('quantity')
            
            if quantity is None or quantity < 1:
                return error_response("Số lượng không hợp lệ")
            
            cart_item = Cart.query.filter_by(
                id=item_id, 
                customer_id=user_id
            ).first()
            
            if not cart_item:
                return error_response("Không tìm thấy món trong giỏ hàng")
            
            cart_item.quantity = quantity
            Cart.query.session.commit()
            
            return success_response("Cập nhật giỏ hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi cập nhật giỏ hàng: {str(e)}")

    @staticmethod
    def remove_from_cart(item_id):
        """Xóa món khỏi giỏ hàng"""
        try:
            user_id = get_jwt_identity()
            
            cart_item = Cart.query.filter_by(
                id=item_id, 
                customer_id=user_id
            ).first()
            
            if not cart_item:
                return error_response("Không tìm thấy món trong giỏ hàng")
            
            Cart.query.session.delete(cart_item)
            Cart.query.session.commit()
            
            return success_response("Xóa món khỏi giỏ hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi xóa món: {str(e)}")

    @staticmethod
    def clear_cart():
        """Xóa toàn bộ giỏ hàng"""
        try:
            user_id = get_jwt_identity()
            
            Cart.query.filter_by(customer_id=user_id).delete()
            Cart.query.session.commit()
            
            return success_response("Xóa giỏ hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi xóa giỏ hàng: {str(e)}")

    @staticmethod
    def get_orders():
        """Lấy danh sách đơn hàng của khách hàng"""
        try:
            user_id = get_jwt_identity()
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            query = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc())
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
    def get_order(order_id):
        """Lấy chi tiết đơn hàng"""
        try:
            user_id = get_jwt_identity()
            
            order = Order.query.filter_by(
                id=order_id, 
                customer_id=user_id
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
    def create_order():
        """Tạo đơn hàng mới"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            # Validate dữ liệu
            validation_result = validate_order_data(data)
            if not validation_result['valid']:
                return error_response(validation_result['message'])
            
            # Kiểm tra giỏ hàng
            cart_items = Cart.query.filter_by(customer_id=user_id).all()
            if not cart_items:
                return error_response("Giỏ hàng trống")
            
            # Kiểm tra tất cả món ăn có available không
            order_items = []
            total_amount = 0
            restaurant_id = None
            
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
            
            # Tạo đơn hàng
            new_order = Order(
                customer_id=user_id,
                restaurant_id=restaurant_id,
                delivery_address=data['delivery_address'],
                delivery_phone=data['delivery_phone'],
                delivery_note=data.get('delivery_note', ''),
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
            
            # Xóa giỏ hàng
            Cart.query.filter_by(customer_id=user_id).delete()
            
            Order.query.session.commit()
            
            return success_response(
                message="Tạo đơn hàng thành công",
                data=new_order.to_dict()
            )
            
        except Exception as e:
            return error_response(f"Lỗi tạo đơn hàng: {str(e)}")

    @staticmethod
    def cancel_order(order_id, data):
        """Hủy đơn hàng"""
        try:
            user_id = get_jwt_identity()
            reason = data.get('reason', '')
            
            order = Order.query.filter_by(
                id=order_id, 
                customer_id=user_id
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
    def create_review():
        """Tạo đánh giá mới cho món ăn"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
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
                Order.customer_id == user_id,
                Order.status.in_(['completed', 'accepted'])
            ).first()
            
            if not has_ordered:
                return error_response("Bạn chưa mua món ăn này, không thể đánh giá")
            
            # Kiểm tra đã đánh giá món ăn này chưa
            existing_review = Review.query.filter_by(
                customer_id=user_id,
                food_id=food_id
            ).first()
            
            if existing_review:
                return error_response("Bạn đã đánh giá món ăn này rồi")
            
            new_review = Review(
                customer_id=user_id,
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
    def get_profile():
        """Lấy thông tin cá nhân"""
        try:
            user_id = get_jwt_identity()
            customer = Customer.query.get(user_id)
            
            if not customer:
                return error_response("Không tìm thấy khách hàng")
            
            return success_response(
                message="Lấy thông tin cá nhân thành công",
                data=customer.to_dict()
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy thông tin cá nhân: {str(e)}")

    @staticmethod
    def update_profile():
        """Cập nhật thông tin cá nhân"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            customer = Customer.query.get(user_id)
            if not customer:
                return error_response("Không tìm thấy khách hàng")
            
            # Cập nhật thông tin
            if 'full_name' in data:
                customer.full_name = data['full_name']
            if 'phone' in data:
                customer.phone = data['phone']
            if 'email' in data:
                customer.email = data['email']
            if 'address' in data:
                customer.address = data['address']
            
            Customer.query.session.commit()
            
            return success_response("Cập nhật thông tin thành công")
            
        except Exception as e:
            return error_response(f"Lỗi cập nhật thông tin: {str(e)}")

    @staticmethod
    def deposit_money():
        """Nạp tiền (mockup)"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            amount = data.get('amount')
            if not amount or amount <= 0:
                return error_response("Số tiền không hợp lệ")
            
            customer = Customer.query.get(user_id)
            if not customer:
                return error_response("Không tìm thấy khách hàng")
            
            # Mockup: cộng tiền vào balance
            customer.balance = (customer.balance or 0) + amount
            
            Customer.query.session.commit()
            
            return success_response(
                message="Nạp tiền thành công",
                data={'new_balance': customer.balance}
            )
            
        except Exception as e:
            return error_response(f"Lỗi nạp tiền: {str(e)}")

    @staticmethod
    def withdraw_money():
        """Rút tiền (mockup)"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            amount = data.get('amount')
            if not amount or amount <= 0:
                return error_response("Số tiền không hợp lệ")
            
            customer = Customer.query.get(user_id)
            if not customer:
                return error_response("Không tìm thấy khách hàng")
            
            if (customer.balance or 0) < amount:
                return error_response("Số dư không đủ")
            
            # Mockup: trừ tiền khỏi balance
            customer.balance -= amount
            
            Customer.query.session.commit()
            
            return success_response(
                message="Rút tiền thành công",
                data={'new_balance': customer.balance}
            )
            
        except Exception as e:
            return error_response(f"Lỗi rút tiền: {str(e)}")
