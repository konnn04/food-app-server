from food_app import db
from food_app.models.review import Review

class ReviewDAO:
    @staticmethod
    def create_review(data):
        review = Review(**data)
        db.session.add(review)
        db.session.commit()
        return review

    @staticmethod
    def get_reviews_for_restaurant(restaurant_id):
        return Review.query.filter_by(restaurant_id=restaurant_id).all()

    @staticmethod
    def get_reviews_for_food(food_id):
        return Review.query.filter_by(food_id=food_id).all()


