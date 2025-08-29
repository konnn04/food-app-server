from food_app import db
from food_app.models.category import Category

class CategoryDAO:
    @staticmethod
    def get_category_by_id(category_id):
        return Category.query.get(category_id)

    @staticmethod
    def get_all_categories():
        return Category.query.all()

    @staticmethod
    def create_category(category_data):
        category = Category(**category_data)
        db.session.add(category)
        db.session.commit()
        return category
