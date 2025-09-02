from flask import Blueprint, request
from food_app.controllers.review_controller import ReviewController
from flasgger import swag_from

review_bp = Blueprint('review', __name__)

@review_bp.route('/', methods=['POST'])
@swag_from({'tags': ['Review'], 'summary': 'Create review'})
def create_review():
    data = request.get_json()
    return ReviewController.create_review(data)

@review_bp.route('/restaurant/<int:restaurant_id>', methods=['GET'])
@swag_from({'tags': ['Review'], 'summary': 'List reviews by restaurant'})
def get_restaurant_reviews(restaurant_id):
    return ReviewController.get_restaurant_reviews(restaurant_id)

@review_bp.route('/food/<int:food_id>', methods=['GET'])
@swag_from({'tags': ['Review'], 'summary': 'List reviews by food'})
def get_food_reviews(food_id):
    return ReviewController.get_food_reviews(food_id)


