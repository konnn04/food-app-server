from food_app import db
from food_app.models.restaurant import Restaurant
from sqlalchemy import or_

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
    def list_restaurants(keyword=None, near=None, max_distance_km=None):
        query = Restaurant.query
        if keyword:
            like = f"%{keyword}%"
            query = query.filter(or_(Restaurant.name.ilike(like), Restaurant.address.ilike(like)))
        if near and max_distance_km:
            lat, lon = near
            import math
            deg_lat = float(max_distance_km) / 111.0
            deg_lon = float(max_distance_km) / (111.0 * max(math.cos(math.radians(lat)), 0.01))
            min_lat, max_lat = lat - deg_lat, lat + deg_lat
            min_lon, max_lon = lon - deg_lon, lon + deg_lon
            query = query.filter(
                Restaurant.latitude.isnot(None), Restaurant.longitude.isnot(None),
                Restaurant.latitude.between(min_lat, max_lat),
                Restaurant.longitude.between(min_lon, max_lon)
            )
        return query

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
