from food_app import db
from food_app.models.food import Food

class FoodDAO:
    @staticmethod
    def get_food_by_id(food_id):
        return Food.query.get(food_id)

    @staticmethod
    def get_foods_by_category(category=None, available_only=True):
        query = Food.query
        if category:
            query = query.filter_by(category_id=category)
        if available_only:
            query = query.filter_by(is_available=True)
        return query.all()

    @staticmethod
    def get_foods_by_restaurant(restaurant_id):
        return Food.query.filter_by(restaurant_id=restaurant_id).all()

    @staticmethod
    def create_food(food_data):
        food = Food(**food_data)
        db.session.add(food)
        db.session.commit()
        return food

    @staticmethod
    def update_food(food, update_data):
        for key, value in update_data.items():
            setattr(food, key, value)
        db.session.commit()
        return food
