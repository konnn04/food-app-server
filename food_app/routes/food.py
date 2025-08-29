from flask import Blueprint, request
from food_app.controllers.food_controller import FoodController

food_bp = Blueprint('food', __name__)

@food_bp.route('/', methods=['GET'])
def get_foods():
    """Lấy danh sách món ăn"""
    category = request.args.get('category')
    available_only = request.args.get('available', 'true').lower() == 'true'
    return FoodController.get_foods(category, available_only)

@food_bp.route('/<int:food_id>', methods=['GET'])
def get_food(food_id):
    """Lấy thông tin một món ăn"""
    return FoodController.get_food(food_id)

@food_bp.route('/', methods=['POST'])
def create_food():
    """Tạo món ăn mới"""
    data = request.get_json()
    return FoodController.create_food(data)

@food_bp.route('/<int:food_id>', methods=['PUT'])
def update_food(food_id):
    """Cập nhật thông tin món ăn"""
    data = request.get_json()
    return FoodController.update_food(food_id, data)

@food_bp.route('/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    """Xóa món ăn"""
    return FoodController.delete_food(food_id)