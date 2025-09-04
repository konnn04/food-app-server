from flask import request
from food_app.models.restaurant import Restaurant
from food_app.models.food import Food
from food_app.utils.distance import calculate_distance
from food_app.utils.responses import success_response, error_response
from food_app.utils.pagination import paginate
from config import Config
from sqlalchemy import or_, and_
from datetime import datetime

class SearchController:
    @staticmethod
    def search():
        try:
            # Lấy parameters từ request
            q = request.args.get('q', '').strip()
            lat = request.args.get('lat', type=float)
            lon = request.args.get('lon', type=float)
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            sort_by = request.args.get('sort_by', 'distance')
            sort_order = request.args.get('sort_order', 'asc')
            page = request.args.get('page', type=int)
            per_page = request.args.get('per_page', type=int)
            
            # Bước 1: Tìm kiếm theo món ăn trước
            food_query = Food.query.filter(Food.available == True)
            
            if q:
                # Tìm theo tên món ăn hoặc tên nhà hàng
                food_query = food_query.join(Restaurant).filter(
                    or_(
                        Food.name.ilike(f'%{q}%'),
                        Food.description.ilike(f'%{q}%'),
                        Restaurant.name.ilike(f'%{q}%')
                    )
                )
            
            # Lọc theo giá nếu có
            if min_price is not None:
                food_query = food_query.filter(Food.price >= min_price)
            if max_price is not None:
                food_query = food_query.filter(Food.price <= max_price)
            
            # Lấy tất cả món ăn thỏa mãn điều kiện
            foods = food_query.all()
            
            # Bước 2: Group món ăn theo nhà hàng
            restaurant_foods = {}
            for food in foods:
                restaurant_id = food.restaurant_id
                if restaurant_id not in restaurant_foods:
                    restaurant_foods[restaurant_id] = []
                restaurant_foods[restaurant_id].append(food)
            
            # Bước 3: Tạo kết quả cho từng nhà hàng
            results = []
            for restaurant_id, restaurant_food_list in restaurant_foods.items():
                restaurant = Restaurant.query.get(restaurant_id)
                if not restaurant or not restaurant.is_active:
                    continue
                
                # Tính khoảng cách nếu có tọa độ
                distance_km = None
                if lat is not None and lon is not None and restaurant.latitude and restaurant.longitude:
                    distance_km = calculate_distance(lat, lon, restaurant.latitude, restaurant.longitude)
                
                # Giới hạn số món ăn hiển thị cho mỗi nhà hàng
                limited_foods = restaurant_food_list[:Config.MAX_FOODS_PER_RESTAURANT]
                
                # Chuyển đổi món ăn thành dict
                searched_foods = []
                for food in limited_foods:
                    food_data = {
                        'id': food.id,
                        'name': food.name,
                        'description': food.description,
                        'price': food.price,
                        'image_url': food.image_url,
                        'available': food.available
                    }
                    searched_foods.append(food_data)
                
                # Tạo dữ liệu nhà hàng
                restaurant_data = restaurant.to_dict(include_sensitive=False)
                restaurant_data['distance_km'] = distance_km
                restaurant_data['searched_foods'] = searched_foods
                results.append(restaurant_data)
            
            # Sắp xếp kết quả
            if sort_by == 'distance' and lat is not None and lon is not None:
                results.sort(key=lambda x: x['distance_km'] if x['distance_km'] is not None else float('inf'))
            elif sort_by == 'price':
                # Sắp xếp theo giá món ăn rẻ nhất của mỗi restaurant
                def get_min_price(restaurant):
                    if not restaurant['searched_foods']:
                        return float('inf')
                    return min(food['price'] for food in restaurant['searched_foods'])
                
                results.sort(key=get_min_price)
            
            if sort_order == 'desc':
                results.reverse()
            
            # Phân trang sử dụng hàm chung
            paginated_results, pagination_info = paginate(results, page, per_page)
            
            return success_response(
                message="Tìm kiếm thành công",
                data={
                    'items': paginated_results,
                    'pagination': pagination_info
                }
            )
            
        except Exception as e:
            return error_response(f"Lỗi tìm kiếm: {str(e)}")
