from flask import Blueprint, request, jsonify
from app import db
from app.models.food import Food
from app.utils.responses import success_response, error_response

food_bp = Blueprint('food', __name__)

@food_bp.route('/', methods=['GET'])
def get_foods():
    try:
        category = request.args.get('category')
        available_only = request.args.get('available', 'true').lower() == 'true'
        
        query = Food.query
        
        if category:
            query = query.filter_by(category=category)
        
        if available_only:
            query = query.filter_by(available=True)
        
        foods = query.all()
        foods_data = [food.to_dict() for food in foods]
        
        return success_response('Lấy danh sách món ăn thành công', foods_data)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@food_bp.route('/<int:food_id>', methods=['GET'])
def get_food(food_id):
    try:
        food = Food.query.get(food_id)
        
        if not food:
            return error_response('Không tìm thấy món ăn', 404)
        
        return success_response('Lấy thông tin món ăn thành công', food.to_dict())
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@food_bp.route('/', methods=['POST'])
def create_food():
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('price'):
            return error_response('Thiếu tên món ăn hoặc giá', 400)
        
        food = Food(
            name=data['name'],
            description=data.get('description'),
            price=float(data['price']),
            category=data.get('category'),
            image_url=data.get('image_url'),
            available=data.get('available', True)
        )
        
        db.session.add(food)
        db.session.commit()
        
        return success_response('Thêm món ăn thành công', food.to_dict(), 201)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)