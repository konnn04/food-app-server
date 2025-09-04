from flask import request
from flask_jwt_extended import get_jwt_identity
from food_app.models.user import User
from food_app.models.food import Food
from food_app.models.order import Order
from food_app.models.review import Review
from food_app.models.restaurant import Restaurant
from food_app.utils.responses import success_response, error_response
from food_app.utils.pagination import paginate
from food_app.utils.validators import validate_food_data
from datetime import datetime, timedelta
from sqlalchemy import and_, func

class StaffController:
    @staticmethod
    def get_foods():
        """Lấy danh sách món ăn của nhà hàng"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
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
    def get_food(food_id):
        """Lấy chi tiết món ăn"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
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
    def create_food():
        """Tạo món ăn mới"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            data = request.get_json()
            
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
    def update_food(food_id):
        """Cập nhật món ăn"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            data = request.get_json()
            
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
    def delete_food(food_id):
        """Xóa món ăn"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
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
    def toggle_food_availability(food_id):
        """Bật/tắt món ăn"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
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
    def get_restaurant():
        """Lấy thông tin nhà hàng"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            restaurant = Restaurant.query.get(user.restaurant_id)
            if not restaurant:
                return error_response("Không tìm thấy nhà hàng")
            
            return success_response(
                message="Lấy thông tin nhà hàng thành công",
                data=restaurant.to_dict()
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy thông tin nhà hàng: {str(e)}")

    @staticmethod
    def update_restaurant():
        """Cập nhật thông tin nhà hàng"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            data = request.get_json()
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
    def update_opening_hours():
        """Cập nhật giờ mở cửa"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            data = request.get_json()
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
    def toggle_restaurant_status():
        """Bật/tắt nhà hàng"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
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
    def get_orders(status=None):
        """Lấy danh sách đơn hàng của nhà hàng"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            page = request.args.get('page', type=int)
            per_page = request.args.get('per_page', type=int)
            
            query = Order.query.filter_by(restaurant_id=user.restaurant_id)
            if status:
                query = query.filter_by(status=status)
            
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
    def get_order(order_id):
        """Lấy chi tiết đơn hàng"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            order = Order.query.filter_by(
                id=order_id, 
                restaurant_id=user.restaurant_id
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
    def accept_order(order_id):
        """Nhận đơn hàng"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            order = Order.query.filter_by(
                id=order_id, 
                restaurant_id=user.restaurant_id
            ).first()
            
            if not order:
                return error_response("Không tìm thấy đơn hàng")
            
            if order.status != 'pending':
                return error_response("Đơn hàng không ở trạng thái chờ xử lý")
            
            order.status = 'accepted'
            order.accepted_at = datetime.utcnow()
            
            Order.query.session.commit()
            
            return success_response("Nhận đơn hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi nhận đơn hàng: {str(e)}")

    @staticmethod
    def complete_order(order_id):
        """Hoàn thành đơn hàng"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
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
            
            order.status = 'completed'
            order.completed_at = datetime.utcnow()
            
            Order.query.session.commit()
            
            return success_response("Hoàn thành đơn hàng thành công")
            
        except Exception as e:
            return error_response(f"Lỗi hoàn thành đơn hàng: {str(e)}")

    @staticmethod
    def cancel_order(order_id, data):
        """Hủy đơn hàng"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.restaurant_id:
                return error_response("Không có quyền truy cập")
            
            reason = data.get('reason', '')
            
            order = Order.query.filter_by(
                id=order_id, 
                restaurant_id=user.restaurant_id
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
    def get_reviews():
        """Lấy đánh giá của nhà hàng"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
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
    def get_revenue(start_date=None, end_date=None):
        """Lấy thống kê doanh thu"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
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
    def get_profile():
        """Lấy thông tin cá nhân"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return error_response("Không tìm thấy người dùng")
            
            return success_response(
                message="Lấy thông tin cá nhân thành công",
                data=user.to_dict()
            )
            
        except Exception as e:
            return error_response(f"Lỗi lấy thông tin cá nhân: {str(e)}")

    @staticmethod
    def update_profile():
        """Cập nhật thông tin cá nhân"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            user = User.query.get(user_id)
            if not user:
                return error_response("Không tìm thấy người dùng")
            
            # Cập nhật thông tin
            if 'full_name' in data:
                user.full_name = data['full_name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'email' in data:
                user.email = data['email']
            if 'address' in data:
                user.address = data['address']
            
            User.query.session.commit()
            
            return success_response("Cập nhật thông tin thành công")
            
        except Exception as e:
            return error_response(f"Lỗi cập nhật thông tin: {str(e)}")
