from food_app.dao import FoodDAO
from food_app.utils.responses import success_response, error_response
from food_app.utils.pagination import paginate
from food_app.models.food import Food
from food_app.models.review import Review
from food_app.models.order_item import OrderItem
from sqlalchemy import func

class FoodController:
    @staticmethod
    def get_foods(category=None, available_only=True):
        """Lấy danh sách món ăn"""
        try:
            from flask import request
            keyword = request.args.get('q')
            page = request.args.get('page', type=int)
            per_page = request.args.get('per_page', type=int)
            lat = request.args.get('lat')
            lon = request.args.get('lon')
            max_km = request.args.get('max_km')
            # Default to HCMC center if not provided
            if not lat or not lon:
                lat = 10.754792
                lon = 106.6952276
            lat = float(lat)
            lon = float(lon)
            near = (lat, lon)
            query = FoodDAO.get_foods(category, available_only, keyword, near, float(max_km) if max_km else None)
            items, meta = paginate(query, page, per_page)

            # Compute distance (km) from provided/default location to restaurant location
            import math
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371.0
                dlat = math.radians(lat2 - lat1)
                dlon = math.radians(lon2 - lon1)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                return R * c

            foods_data = []
            for food in items:
                data = food.to_dict()
                rest = food.restaurant
                distance_km = None
                if rest and rest.latitude is not None and rest.longitude is not None:
                    distance_km = round(haversine(lat, lon, rest.latitude, rest.longitude), 3)
                data['distance_km'] = distance_km
                
                # Thêm thông tin distance vào restaurant object nếu có
                if data.get('restaurant') and distance_km is not None:
                    data['restaurant']['distance_km'] = distance_km
                
                foods_data.append(data)

            return success_response('Lấy danh sách món ăn thành công', {'items': foods_data, 'meta': meta})

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_food(food_id):
        """Lấy thông tin một món ăn"""
        try:
            food = FoodDAO.get_food_by_id(food_id)

            if not food:
                return error_response('Không tìm thấy món ăn', 404)

            return success_response('Lấy thông tin món ăn thành công', food.to_dict())

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_food_detail(food_id):
        """Lấy chi tiết món ăn với thông tin bổ sung"""
        try:
            food = Food.query.get(food_id)
            if not food:
                return error_response('Không tìm thấy món ăn', 404)

            # Tính số lượng đã bán
            sold_count = OrderItem.query.filter_by(food_id=food_id).with_entities(
                func.sum(OrderItem.quantity)
            ).scalar() or 0

            # Tính đánh giá trung bình
            avg_rating = Review.query.filter_by(food_id=food_id).with_entities(
                func.avg(Review.rating)
            ).scalar() or 0

            # Đếm số đánh giá
            review_count = Review.query.filter_by(food_id=food_id).count()

            # Lấy đánh giá gần đây
            recent_reviews = Review.query.filter_by(food_id=food_id)\
                .order_by(Review.created_at.desc())\
                .limit(5).all()

            food_data = food.to_dict()
            food_data.update({
                'sold_count': sold_count,
                'avg_rating': round(float(avg_rating), 1) if avg_rating else 0,
                'review_count': review_count,
                'recent_reviews': [review.to_dict() for review in recent_reviews],
                'restaurant': food.restaurant.to_dict() if food.restaurant else None
            })

            return success_response('Lấy chi tiết món ăn thành công', food_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def create_food(data):
        """Tạo món ăn mới"""
        try:
            if not data.get('name') or not data.get('price'):
                return error_response('Thiếu tên món ăn hoặc giá', 400)

            food_data = {
                'name': data['name'],
                'description': data.get('description'),
                'price': float(data['price']),
                'category': data.get('category'),
                'image_url': data.get('image_url'),
                'available': data.get('available', True),
                'restaurant_id': data.get('restaurant_id')  # Cần thêm validation
            }

            food = FoodDAO.create_food(food_data)

            return success_response('Thêm món ăn thành công', food.to_dict(), 201)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def update_food(food_id, data):
        """Cập nhật thông tin món ăn"""
        try:
            food = FoodDAO.get_food_by_id(food_id)

            if not food:
                return error_response('Không tìm thấy món ăn', 404)

            update_data = {}
            if 'name' in data:
                update_data['name'] = data['name']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'price' in data:
                update_data['price'] = float(data['price'])
            if 'category' in data:
                update_data['category'] = data['category']
            if 'image_url' in data:
                update_data['image_url'] = data['image_url']
            if 'available' in data:
                update_data['available'] = data['available']

            updated_food = FoodDAO.update_food(food, update_data)

            return success_response('Cập nhật món ăn thành công', updated_food.to_dict())

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def delete_food(food_id):
        """Xóa món ăn"""
        try:
            from food_app import db
            food = FoodDAO.get_food_by_id(food_id)

            if not food:
                return error_response('Không tìm thấy món ăn', 404)

            db.session.delete(food)
            db.session.commit()

            return success_response('Xóa món ăn thành công')

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)
