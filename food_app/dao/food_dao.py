from food_app import db
from food_app.models.food import Food
from food_app.models.topping import Topping
from food_app.models.restaurant import Restaurant

class FoodDAO:
    @staticmethod
    def get_food_by_id(food_id):
        return Food.query.get(food_id)

    @staticmethod
    def get_foods(category=None, available_only=True, keyword=None, near=None, max_distance_km=None):
        query = Food.query
        if category:
            from food_app.models.category import Category
            query = query.join(Food.categories).filter(Category.id == category)
        if available_only:
            query = query.filter(Food.available.is_(True))
        if keyword:
            like = f"%{keyword}%"
            query = query.filter(Food.name.ilike(like))
        if near and max_distance_km:
            lat, lon = near
            # Simple bounding box prefilter to avoid heavy joins
            # ~1 deg lat ~= 111km, lon scaled by cos(lat)
            deg_lat = float(max_distance_km) / 111.0
            import math
            deg_lon = float(max_distance_km) / (111.0 * max(math.cos(math.radians(lat)), 0.01))
            min_lat, max_lat = lat - deg_lat, lat + deg_lat
            min_lon, max_lon = lon - deg_lon, lon + deg_lon
            query = query.join(Restaurant).filter(
                Restaurant.latitude.isnot(None), Restaurant.longitude.isnot(None),
                Restaurant.latitude.between(min_lat, max_lat),
                Restaurant.longitude.between(min_lon, max_lon)
            )
        return query

    @staticmethod
    def get_foods_by_restaurant(restaurant_id):
        return Food.query.filter_by(restaurant_id=restaurant_id)

    @staticmethod
    def create_food(food_data):
        toppings = food_data.pop('toppings', None)
        food = Food(**food_data)
        if toppings:
            food.toppings = Topping.query.filter(Topping.id.in_(toppings)).all()
        db.session.add(food)
        db.session.commit()
        return food

    @staticmethod
    def update_food(food, update_data):
        toppings = update_data.pop('toppings', None)
        for key, value in update_data.items():
            setattr(food, key, value)
        if toppings is not None:
            food.toppings = Topping.query.filter(Topping.id.in_(toppings)).all()
        db.session.commit()
        return food
