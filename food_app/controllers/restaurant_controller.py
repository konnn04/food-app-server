from food_app.dao import RestaurantDAO, UserDAO
from food_app.utils.responses import success_response, error_response
from flask_jwt_extended import get_jwt_identity
from food_app.models.restaurant_staff import restaurant_staff
from food_app import db
from food_app.utils.pagination import paginate
from food_app.models.restaurant import Restaurant
from food_app.models.food import Food
from food_app.models.review import Review
from food_app.models.order import Order
from sqlalchemy import func
from food_app.models.order_item import OrderItem

class RestaurantController:
    @staticmethod
    def create_restaurant(data, current_user):
        """Owner tạo restaurant mới (duy nhất 1)"""
        try:
            # Kiểm tra quyền owner
            if current_user.role != 'owner':
                return error_response('Chỉ owner mới có thể tạo nhà hàng', 403)

            # Kiểm tra owner đã có restaurant chưa
            if current_user.owned_restaurant:
                return error_response('Bạn đã có nhà hàng rồi. Mỗi owner chỉ được tạo 1 nhà hàng.', 400)

            # Validation
            required_fields = ['name', 'address', 'phone', 'email', 'tax_code']
            for field in required_fields:
                if not data.get(field):
                    return error_response(f'Thiếu thông tin bắt buộc: {field}', 400)

            # Tạo restaurant data
            restaurant_data = {
                'name': data['name'],
                'address': data['address'],
                'phone': data['phone'],
                'email': data['email'],
                'description': data.get('description'),
                'image_url': data.get('image_url'),
                'opening_hours': data.get('opening_hours', {}),
                'tax_code': data['tax_code'],
                'owner_id': current_user.id
            }

            restaurant = RestaurantDAO.create_restaurant(restaurant_data)
            
            return success_response('Tạo nhà hàng thành công', restaurant.to_dict(), 201)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_my_restaurant(current_user):
        """Lấy thông tin restaurant của owner"""
        try:
            if current_user.role != 'owner':
                return error_response('Chỉ owner mới có quyền xem', 403)

            if not current_user.owned_restaurant:
                return error_response('Bạn chưa tạo nhà hàng. Vui lòng tạo nhà hàng trước.', 404)

            restaurant = current_user.owned_restaurant
            
            return success_response('Lấy thông tin nhà hàng thành công', restaurant.to_dict())

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def list_restaurants():
        try:
            from flask import request
            keyword = request.args.get('q')
            page = request.args.get('page', type=int)
            per_page = request.args.get('per_page', type=int)
            lat = request.args.get('lat')
            lon = request.args.get('lon')
            max_km = request.args.get('max_km')
            near = (float(lat), float(lon)) if lat and lon else None
            query = RestaurantDAO.list_restaurants(keyword, near, float(max_km) if max_km else None)
            items, meta = paginate(query, page, per_page)
            return success_response('Lấy danh sách nhà hàng thành công', {'items': [r.to_dict() for r in items], 'meta': meta})
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_restaurant_detail(restaurant_id):
        """Lấy chi tiết nhà hàng với thông tin bổ sung"""
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            if not restaurant:
                return error_response('Không tìm thấy nhà hàng', 404)

            # Tính tổng doanh thu
            total_revenue = Order.query.filter_by(
                restaurant_id=restaurant_id, 
                status='completed'
            ).with_entities(
                func.sum(Order.total_amount)
            ).scalar() or 0

            # Đếm số đơn hàng đã hoàn thành
            completed_orders = Order.query.filter_by(
                restaurant_id=restaurant_id, 
                status='completed'
            ).count()

            # Tính đánh giá trung bình
            avg_rating = Review.query.filter_by(restaurant_id=restaurant_id).with_entities(
                func.avg(Review.rating)
            ).scalar() or 0

            # Đếm số đánh giá
            review_count = Review.query.filter_by(restaurant_id=restaurant_id).count()

            # Đếm số món ăn
            food_count = Food.query.filter_by(restaurant_id=restaurant_id).count()

            # Lấy đánh giá gần đây
            recent_reviews = Review.query.filter_by(restaurant_id=restaurant_id)\
                .order_by(Review.created_at.desc())\
                .limit(5).all()

            # Lấy món ăn nổi bật (bán chạy nhất)
            top_foods = db.session.query(Food, func.sum(OrderItem.quantity).label('total_sold'))\
                .join(OrderItem, Food.id == OrderItem.food_id)\
                .filter(Food.restaurant_id == restaurant_id)\
                .group_by(Food.id)\
                .order_by(func.sum(OrderItem.quantity).desc())\
                .limit(5).all()

            restaurant_data = restaurant.to_dict()
            restaurant_data.update({
                'total_revenue': float(total_revenue),
                'completed_orders': completed_orders,
                'avg_rating': round(float(avg_rating), 1) if avg_rating else 0,
                'review_count': review_count,
                'food_count': food_count,
                'recent_reviews': [review.to_dict() for review in recent_reviews],
                'top_foods': [
                    {
                        'id': food.id,
                        'name': food.name,
                        'price': food.price,
                        'image_url': food.image_url,
                        'total_sold': total_sold
                    } for food, total_sold in top_foods
                ]
            })

            return success_response('Lấy chi tiết nhà hàng thành công', restaurant_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def update_restaurant(data, current_user):
        """Owner cập nhật restaurant của mình"""
        try:
            if current_user.role != 'owner':
                return error_response('Chỉ owner mới có quyền cập nhật', 403)

            if not current_user.owned_restaurant:
                return error_response('Bạn chưa tạo nhà hàng', 404)

            restaurant = current_user.owned_restaurant

            # Cập nhật dữ liệu
            update_data = {}
            allowed_fields = [
                'name', 'address', 'phone', 'email', 'description', 
                'image_url', 'opening_hours', 'is_active'
            ]
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]

            updated_restaurant = RestaurantDAO.update_restaurant(restaurant, update_data)
            
            return success_response('Cập nhật nhà hàng thành công', updated_restaurant.to_dict())

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def add_staff(data, current_user):
        """Owner/manager thêm nhân viên vào nhà hàng (không cần invitation)"""
        try:
            if not current_user.can_invite_staff():
                return error_response('Bạn không có quyền thêm nhân viên', 403)

            if not current_user.owned_restaurant:
                return error_response('Bạn chưa tạo nhà hàng', 404)

            username = data.get('username')
            role = data.get('role', 'staff')
            if not username:
                return error_response('Thiếu username của nhân viên', 400)
            if role not in ['staff', 'manager']:
                return error_response('Vai trò phải là staff hoặc manager', 400)

            staff_user = UserDAO.get_user_by_username(username)
            if not staff_user:
                return error_response('Không tìm thấy user với username này', 404)

            # Thêm vào bảng liên kết nếu chưa tồn tại
            restaurant = current_user.owned_restaurant
            link_exists = db.session.execute(
                db.select(restaurant_staff)
                .where(restaurant_staff.c.user_id == staff_user.id)
                .where(restaurant_staff.c.restaurant_id == restaurant.id)
            ).first()
            if link_exists:
                return error_response('Nhân viên đã thuộc nhà hàng này', 400)

            db.session.execute(
                restaurant_staff.insert().values(
                    user_id=staff_user.id,
                    restaurant_id=restaurant.id,
                    role=role
                )
            )
            db.session.commit()

            return success_response('Thêm nhân viên thành công', staff_user.to_dict())

        except Exception as e:
            db.session.rollback()
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def remove_staff(user_id, current_user):
        """Owner/manager xóa nhân viên khỏi nhà hàng"""
        try:
            if not current_user.can_invite_staff():
                return error_response('Bạn không có quyền xóa nhân viên', 403)
            if not current_user.owned_restaurant:
                return error_response('Bạn chưa tạo nhà hàng', 404)

            restaurant = current_user.owned_restaurant
            deleted = db.session.execute(
                restaurant_staff.delete()
                .where(restaurant_staff.c.user_id == user_id)
                .where(restaurant_staff.c.restaurant_id == restaurant.id)
            )
            if deleted.rowcount == 0:
                db.session.rollback()
                return error_response('Nhân viên không thuộc nhà hàng này', 404)
            db.session.commit()
            return success_response('Đã xóa nhân viên khỏi nhà hàng')
        except Exception as e:
            db.session.rollback()
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    # Invitation-related endpoints removed

    # Invitation handling removed

    @staticmethod
    def get_restaurant_staff(current_user):
        """Lấy danh sách staff/manager của restaurant"""
        try:
            if current_user.role == 'owner':
                restaurant = current_user.owned_restaurant
            elif current_user.role in ['manager', 'staff']:
                restaurant = current_user.restaurants[0] if current_user.restaurants else None
            else:
                return error_response('Không có quyền truy cập', 403)

            if not restaurant:
                return error_response('Không tìm thấy nhà hàng', 404)

            staff_list = [user.to_dict() for user in restaurant.staff_users if user.role in ['staff', 'manager']]

            return success_response('Lấy danh sách nhân viên thành công', staff_list)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)