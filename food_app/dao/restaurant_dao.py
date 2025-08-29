from food_app import db
from food_app.models.restaurant import Restaurant

class RestaurantDAO:
    @staticmethod
    def get_restaurant_by_id(restaurant_id):
        return Restaurant.query.get(restaurant_id)

    @staticmethod
    def get_restaurant_by_owner(owner_id):
        return Restaurant.query.filter_by(owner_id=owner_id).first()

    @staticmethod
    def get_restaurants_by_status(status):
        return Restaurant.query.filter_by(approval_status=status).all()

    @staticmethod
    def create_restaurant(restaurant_data):
        restaurant = Restaurant(**restaurant_data)
        db.session.add(restaurant)
        db.session.commit()
        return restaurant

    @staticmethod
    def update_restaurant(restaurant, update_data):
        for key, value in update_data.items():
            setattr(restaurant, key, value)
        db.session.commit()
        return restaurant
