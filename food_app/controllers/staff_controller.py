from flask import request
from food_app.models.user import User
from food_app.models.food import Food
from food_app.models.order import Order
from food_app.models.review import Review
from food_app.models.restaurant import Restaurant
from food_app.utils.responses import success_response, error_response
from food_app.utils.pagination import paginate
from food_app.utils.validators import validate_food_data
from food_app.utils.jwt_service import get_user_id_from_jwt, get_user_type_from_jwt
from datetime import datetime, timedelta
from sqlalchemy import and_, func

class StaffController:
    @staticmethod
    def create_restaurant(data, current_user):
        """Tạo và liên kết nhà hàng đầu tiên cho user chưa có restaurant.
        Yêu cầu: JWT staff; KHÔNG yêu cầu đã liên kết nhà hàng.
        """
        try:
            if not current_user:
                return error_response("Không tìm thấy người dùng")

            if current_user.restaurant_id:
                return error_response("Tài khoản đã liên kết nhà hàng")

            name = data.get('name')
            address = data.get('address')
            phone = data.get('phone')
            email = data.get('email')
            image_url = data.get('image_url')
            description = data.get('description', '')

            if not name or not address or not phone:
                return error_response("Thiếu thông tin bắt buộc: name, address, phone")

            # Tạo nhà hàng và liên kết owner là current_user
            restaurant = Restaurant(
                name=name,
                address=address,
                phone=phone,
                email=email,
                description=description,
                image_url=image_url,
                is_active=True,
                owner_id=current_user.id,
                opening_hours="07:00-22:00",
            )

            Restaurant.query.session.add(restaurant)
            Restaurant.query.session.flush()

            # Liên kết vào user
            current_user.restaurant_id = restaurant.id
            User.query.session.commit()

            return success_response(
                message="Tạo nhà hàng và liên kết thành công",
                data=restaurant.to_dict(include_sensitive=True)
            )
        except Exception as e:
            return error_response(f"Lỗi tạo nhà hàng: {str(e)}")
    @staticmethod
    def get_foods(current_user=None):
        """Lấy danh sách món ăn của nhà hàng"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            page = request.args.get('page', type=int)
            per_page = request.args.get('per_page', type=int)
            
            query = Food.query.filter_by(restaurant_id=user.restaurant_id).order_by(Food.created_at.desc())
            foods, pagination_info = paginate(query, page, per_page)
            
            foods_data = [food.to_dict() for food in foods]
            
            return success_response(
                message="Lấy danh sách món ăn thành công",
                data={
                    'items': foods_data,
                    'pagination': pagination_info
                }
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy danh sách món ăn: {str(e)}")

    @staticmethod
    def get_food(food_id, current_user=None):
        """Lấy chi tiết món ăn"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            food = Food.query.filter_by(
                id=food_id, 
                restaurant_id=user.restaurant_id
            ).first()
            
            if not food:
                return error_response("Không tìm thấy món ăn")
            
            return success_response(
                message="Lấy chi tiết món ăn thành công",
                data=food.to_dict()
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy chi tiết món ăn: {str(e)}")

    @staticmethod
    def create_food(data=None, current_user=None):
        """Tạo món ăn mới"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            data = data or request.get_json()
            
            # Validate dữ liệu
            validation_result = validate_food_data(data)
            if not validation_result['valid']:
                return error_response(validation_result['message'])
            
            new_food = Food(
                name=data['name'],
                description=data.get('description', ''),
                price=data['price'],
                image_url=data.get('image_url', ''),
                restaurant_id=user.restaurant_id,
                available=data.get('available', True)
            )
            
            Food.query.session.add(new_food)
            Food.query.session.commit()
            
            return success_response(
                message="Tạo món ăn thành công",
                data=new_food.to_dict()
            )
            
        except Exception as e:
            return error_response(f"Lỗi tạo món ăn: {str(e)}")

    @staticmethod
    def update_food(food_id, data=None, current_user=None):
        """Cập nhật món ăn"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            data = data or request.get_json()
            
            food = Food.query.filter_by(
                id=food_id, 
                restaurant_id=user.restaurant_id
            ).first()
            
            if not food:
                return error_response("Không tìm thấy món ăn")
            
            # Cập nhật thông tin
            if 'name' in data:
                food.name = data['name']
            if 'description' in data:
                food.description = data['description']
            if 'price' in data:
                food.price = data['price']
            if 'image_url' in data:
                food.image_url = data['image_url']
            if 'available' in data:
                food.available = data['available']
            
            Food.query.session.commit()
            
            return success_response(
                message="Cập nhật món ăn thành công",
                data=food.to_dict()
            )
            
        except Exception as e:
            return error_response(f"Lỗi cập nhật món ăn: {str(e)}")

    @staticmethod
    def delete_food(food_id, current_user=None):
        """Xóa món ăn"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            food = Food.query.filter_by(
                id=food_id, 
                restaurant_id=user.restaurant_id
            ).first()
            
            if not food:
                return error_response("Không tìm thấy món ăn")
            
            Food.query.session.delete(food)
            Food.query.session.commit()
            
            return success_response("Xóa món ăn thành công")
            
        except Exception as e:
            return error_response(f"Lỗi xóa món ăn: {str(e)}")

    @staticmethod
    def toggle_food_availability(food_id, current_user=None):
        """Bật/tắt món ăn"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            food = Food.query.filter_by(
                id=food_id, 
                restaurant_id=user.restaurant_id
            ).first()
            
            if not food:
                return error_response("Không tìm thấy món ăn")
            
            food.available = not food.available
            Food.query.session.commit()
            
            status = "bật" if food.available else "tắt"
            return success_response(f"{status.capitalize()} món ăn thành công")
            
        except Exception as e:
            return error_response(f"Lỗi thay đổi trạng thái món ăn: {str(e)}")

    @staticmethod
    def get_restaurant(current_user=None):
        """Lấy thông tin nhà hàng"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            restaurant = Restaurant.query.get(user.restaurant_id)
            if not restaurant:
                return error_response("Không tìm thấy nhà hàng")
            
            return success_response(
                message="Lấy thông tin nhà hàng thành công",
                data=restaurant.to_dict(include_sensitive=True)
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy thông tin nhà hàng: {str(e)}")

    @staticmethod
    def update_restaurant(data=None, current_user=None):
        """Cập nhật thông tin nhà hàng"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            data = data or request.get_json()
            restaurant = Restaurant.query.get(user.restaurant_id)
            
            if not restaurant:
                return error_response("Không tìm thấy nhà hàng")
            
            # Cập nhật thông tin
            if 'name' in data:
                restaurant.name = data['name']
            if 'description' in data:
                restaurant.description = data['description']
            if 'phone' in data:
                restaurant.phone = data['phone']
            if 'email' in data:
                restaurant.email = data['email']
            if 'address' in data:
                restaurant.address = data['address']
            if 'image_url' in data:
                restaurant.image_url = data['image_url']
            
            Restaurant.query.session.commit()
            
            return success_response("Cập nhật thông tin nhà hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi cập nhật thông tin nhà hàng: {str(e)}")

    @staticmethod
    def update_opening_hours(data=None, current_user=None):
        """Cập nhật giờ mở cửa"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            data = data or request.get_json()
            opening_hours = data.get('opening_hours')
            
            if not opening_hours:
                return error_response("Thiếu thông tin giờ mở cửa")
            
            restaurant = Restaurant.query.get(user.restaurant_id)
            if not restaurant:
                return error_response("Không tìm thấy nhà hàng")
            
            restaurant.opening_hours = opening_hours
            Restaurant.query.session.commit()
            
            return success_response("Cập nhật giờ mở cửa thành công")
            
        except Exception as e:
            return error_response(f"Lỗi cập nhật giờ mở cửa: {str(e)}")

    @staticmethod
    def toggle_restaurant_status(current_user=None):
        """Bật/tắt nhà hàng"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            restaurant = Restaurant.query.get(user.restaurant_id)
            if not restaurant:
                return error_response("Không tìm thấy nhà hàng")
            
            restaurant.is_active = not restaurant.is_active
            Restaurant.query.session.commit()
            
            status = "bật" if restaurant.is_active else "tắt"
            return success_response(f"{status.capitalize()} nhà hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi thay đổi trạng thái nhà hàng: {str(e)}")

    @staticmethod
    def get_orders(status=None, current_user=None):
        """Lấy danh sách đơn hàng của nhà hàng"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            page = request.args.get('page', type=int)
            per_page = request.args.get('per_page', type=int)
            
            query = Order.query.filter_by(restaurant_id=user.restaurant_id)
            if status:
                # Tôn trọng filter client gửi lên
                query = query.filter_by(status=status)
            else:
                # Mặc định KHÔNG hiển thị đơn chưa thanh toán cho nhà hàng
                query = query.filter(Order.status != 'pending')
            
            query = query.order_by(Order.created_at.desc())
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
            return error_response(f"Lỗi lấy danh sách đơn hàng: {str(e)}")

    @staticmethod
    def get_order(order_id, current_user=None):
        """Lấy chi tiết đơn hàng"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            order = Order.query.filter_by(
                id=order_id, 
                restaurant_id=user.restaurant_id
            ).first()
            
            if not order:
                return error_response("Không tìm thấy đơn hàng")
            # Ẩn đơn chưa thanh toán khỏi phía nhà hàng
            if order.status == 'pending':
                return error_response("Không có quyền truy cập đơn này")
            
            return success_response(
                message="Lấy chi tiết đơn hàng thành công",
                data=order.to_dict()
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy chi tiết đơn hàng: {str(e)}")

    @staticmethod
    def accept_order(order_id, current_user=None):
        """Nhận đơn hàng"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            order = Order.query.filter_by(
                id=order_id, 
                restaurant_id=user.restaurant_id
            ).first()
            
            if not order:
                return error_response("Không tìm thấy đơn hàng")
            
            # Chỉ cho nhận khi đã thanh toán (paid)
            if order.status != 'paid':
                return error_response("Đơn hàng chưa thanh toán hoặc đã được xử lý")
            
            order.status = 'accepted'
            order.accepted_at = datetime.utcnow()
            
            Order.query.session.commit()
            
            return success_response("Nhận đơn hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi nhận đơn hàng: {str(e)}")

    @staticmethod
    def complete_order(order_id, current_user=None):
        """Hoàn thành đơn hàng"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            order = Order.query.filter_by(
                id=order_id, 
                restaurant_id=user.restaurant_id
            ).first()
            
            if not order:
                return error_response("Không tìm thấy đơn hàng")
            
            if order.status != 'done':
                return error_response("Đơn hàng chưa ở trạng thái 'done'")
            
            order.status = 'completed'
            order.completed_at = datetime.utcnow()

            # Credit restaurant owner wallet on completion
            try:
                restaurant = Restaurant.query.get(order.restaurant_id)
                if restaurant and getattr(restaurant, 'owner_id', None):
                    owner = User.query.get(restaurant.owner_id)
                    if owner:
                        owner.balance = float(owner.balance or 0) + float(order.total_amount or 0)
            except Exception:
                # Continue commit even if crediting fails to avoid blocking order flow
                pass

            Order.query.session.commit()
            
            return success_response("Hoàn thành đơn hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi hoàn thành đơn hàng: {str(e)}")

    @staticmethod
    def mark_done(order_id, current_user=None):
        """Bếp xong món, bàn giao cho vận chuyển"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            order = Order.query.filter_by(
                id=order_id, 
                restaurant_id=user.restaurant_id
            ).first()
            
            if not order:
                return error_response("Không tìm thấy đơn hàng")
            
            if order.status != 'accepted':
                return error_response("Đơn hàng chưa được nhận")

            order.status = 'done'
            Order.query.session.commit()
            
            return success_response("Đánh dấu đơn đã xong món thành công")
        except Exception as e:
            return error_response(f"Lỗi đánh dấu done: {str(e)}")

    @staticmethod
    def cancel_order(order_id, data, current_user=None):
        """Hủy đơn hàng"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            reason = data.get('reason', '')
            
            order = Order.query.filter_by(
                id=order_id, 
                restaurant_id=user.restaurant_id
            ).first()
            
            if not order:
                return error_response("Không tìm thấy đơn hàng")
            
            # Chỉ cho phép hủy sau khi đã tiếp nhận hoặc khi đã xong món (trước khi hoàn thành)
            if order.status not in ['accepted', 'done']:
                return error_response("Không thể hủy đơn hàng ở trạng thái này")
            
            order.status = 'cancelled'
            order.cancel_reason = reason
            order.cancelled_at = datetime.utcnow()

            # Refund customer wallet on cancel (for paid/accepted/done orders not completed)
            try:
                from food_app.models.customer import Customer
                customer = Customer.query.get(order.customer_id)
                if customer:
                    customer.balance = float(customer.balance or 0) + float(order.total_amount or 0)
            except Exception:
                pass

            Order.query.session.commit()
            
            return success_response("Hủy đơn hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi hủy đơn hàng: {str(e)}")

    @staticmethod
    def get_reviews(current_user=None):
        """Lấy đánh giá của nhà hàng"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            page = request.args.get('page', type=int)
            per_page = request.args.get('per_page', type=int)
            
            query = Review.query.filter_by(restaurant_id=user.restaurant_id).order_by(Review.created_at.desc())
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
    def get_revenue(start_date=None, end_date=None, current_user=None):
        """Lấy thống kê doanh thu"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            # Parse dates
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            else:
                start_date = datetime.now() - timedelta(days=30)
            
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                end_date = datetime.now()
            
            # Query completed orders
            orders = Order.query.filter(
                and_(
                    Order.restaurant_id == user.restaurant_id,
                    Order.status == 'completed',
                    Order.completed_at >= start_date,
                    Order.completed_at <= end_date
                )
            ).all()
            
            total_revenue = sum(order.total_amount for order in orders)
            order_count = len(orders)
            
            # Daily revenue
            daily_revenue = Order.query.with_entities(
                func.date(Order.completed_at).label('date'),
                func.sum(Order.total_amount).label('revenue'),
                func.count(Order.id).label('orders')
            ).filter(
                and_(
                    Order.restaurant_id == user.restaurant_id,
                    Order.status == 'completed',
                    Order.completed_at >= start_date,
                    Order.completed_at <= end_date
                )
            ).group_by(func.date(Order.completed_at)).all()
            
            daily_data = []
            for day in daily_revenue:
                daily_data.append({
                    'date': day.date.strftime('%Y-%m-%d'),
                    'revenue': float(day.revenue),
                    'orders': day.orders
                })
            
            return success_response(
                message="Lấy thống kê doanh thu thành công",
                data={
                    'total_revenue': total_revenue,
                    'order_count': order_count,
                    'period': {
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d')
                    },
                    'daily_revenue': daily_data
                }
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy thống kê doanh thu: {str(e)}")

    @staticmethod
    def get_profile(current_user=None):
        """Lấy thông tin cá nhân"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            
            if not user:
                return error_response("Không tìm thấy người dùng")
            
            return success_response(
                message="Lấy thông tin cá nhân thành công",
                data=user.to_dict()
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy thông tin cá nhân: {str(e)}")

    @staticmethod
    def update_profile(data=None, current_user=None):
        """Cập nhật thông tin cá nhân"""
        try:
            user = current_user or User.query.get(get_user_id_from_jwt())
            data = data or request.get_json()
            if not user:
                return error_response("Không tìm thấy người dùng")
            
            # Cập nhật thông tin
            # Ưu tiên first_name/last_name; nếu gửi full_name thì tách ra
            full_name = data.get('full_name')
            if full_name and (not data.get('first_name') and not data.get('last_name')):
                parts = str(full_name).strip().split()
                if len(parts) == 1:
                    user.first_name = parts[0]
                    user.last_name = ''
                else:
                    user.first_name = ' '.join(parts[:-1])
                    user.last_name = parts[-1]
            else:
                if 'first_name' in data:
                    user.first_name = data['first_name']
                if 'last_name' in data:
                    user.last_name = data['last_name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'email' in data:
                user.email = data['email']
            if 'address' in data:
                user.address = data['address']
            
            # Nếu đã có tối thiểu họ hoặc tên (ưu tiên cả hai), đánh dấu đã cập nhật
            has_any_profile_field = bool((user.first_name or '').strip() or (user.last_name or '').strip() or (user.phone or '').strip() or (user.email or '').strip() or (user.address or '').strip())
            if has_any_profile_field:
                user.is_need_update = False

            User.query.session.commit()
            
            return success_response("Cập nhật thông tin thành công")
            
        except Exception as e:
            return error_response(f"Lỗi cập nhật thông tin: {str(e)}")
