from food_app.dao import FoodDAO
from food_app.utils.responses import success_response, error_response

class FoodController:
    @staticmethod
    def get_foods(category=None, available_only=True):
        """Lấy danh sách món ăn"""
        try:
            foods = FoodDAO.get_foods_by_category(category, available_only)
            foods_data = [food.to_dict() for food in foods]

            return success_response('Lấy danh sách món ăn thành công', foods_data)

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
