from flask import Blueprint, request
from food_app.controllers.food_controller import FoodController
from flasgger import swag_from

food_bp = Blueprint('food', __name__)

@food_bp.route('/', methods=['GET'])
@swag_from({'tags': ['Food'], 'summary': 'List foods with restaurant info', 'parameters': [
    {'in': 'query', 'name': 'category', 'schema': {'type': 'integer'}},
    {'in': 'query', 'name': 'available', 'schema': {'type': 'boolean'}},
    {'in': 'query', 'name': 'q', 'schema': {'type': 'string'}},
    {'in': 'query', 'name': 'page', 'schema': {'type': 'integer'}},
    {'in': 'query', 'name': 'per_page', 'schema': {'type': 'integer'}},
    {'in': 'query', 'name': 'lat', 'schema': {'type': 'number', 'format': 'float'}, 'description': 'Default 10.754792'},
    {'in': 'query', 'name': 'lon', 'schema': {'type': 'number', 'format': 'float'}, 'description': 'Default 106.6952276'},
    {'in': 'query', 'name': 'max_km', 'schema': {'type': 'number', 'format': 'float'}}
], 'responses': {
    '200': {
        'description': 'Success',
        'schema': {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'message': {'type': 'string'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'items': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'},
                                    'price': {'type': 'number'},
                                    'distance_km': {'type': 'number'},
                                    'restaurant': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'integer'},
                                            'name': {'type': 'string'},
                                            'address': {'type': 'string'},
                                            'phone': {'type': 'string'},
                                            'latitude': {'type': 'number'},
                                            'longitude': {'type': 'number'},
                                            'distance_km': {'type': 'number'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}})
def get_foods():
    """Lấy danh sách món ăn"""
    category = request.args.get('category')
    available_only = request.args.get('available', 'true').lower() == 'true'
    return FoodController.get_foods(category, available_only)

@food_bp.route('/<int:food_id>/', methods=['GET'])
@swag_from({'tags': ['Food'], 'summary': 'Get food detail with additional info'})
def get_food(food_id):
    """Lấy chi tiết món ăn với thông tin bổ sung"""
    return FoodController.get_food_detail(food_id)

@food_bp.route('/', methods=['POST'])
@swag_from({'tags': ['Food'], 'summary': 'Create food', 'responses': {'201': {'description': 'Created'}}})
def create_food():
    """Tạo món ăn mới"""
    data = request.get_json()
    return FoodController.create_food(data)

@food_bp.route('/<int:food_id>/', methods=['PUT'])
@swag_from({'tags': ['Food'], 'summary': 'Update food'})
def update_food(food_id):
    """Cập nhật thông tin món ăn"""
    data = request.get_json()
    return FoodController.update_food(food_id, data)

@food_bp.route('/<int:food_id>/', methods=['DELETE'])
@swag_from({'tags': ['Food'], 'summary': 'Delete food'})
def delete_food(food_id):
    """Xóa món ăn"""
    return FoodController.delete_food(food_id)