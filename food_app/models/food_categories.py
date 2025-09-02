from food_app import db
from datetime import datetime

food_categories = db.Table('food_categories',
    db.Column('food_id', db.Integer, db.ForeignKey('foods.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    db.Column('is_primary', db.Boolean, default=False)
)