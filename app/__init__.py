from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_admin import Admin
from config import config

db = SQLAlchemy()
jwt = JWTManager()
flask_admin = Admin(name='Food Ordering Admin', template_mode='bootstrap4')

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Khởi tạo extensions
    db.init_app(app)
    CORS(app)
    jwt.init_app(app)
    flask_admin.init_app(app)
    
    # Đăng ký blueprints
    from app.routes.auth import auth_bp
    from app.routes.food import food_bp
    from app.routes.order import order_bp
    from app.routes.admin_api import admin_api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(food_bp, url_prefix='/api/food')
    app.register_blueprint(order_bp, url_prefix='/api/order')
    app.register_blueprint(admin_api_bp, url_prefix='/api/admin')
    
    # Tạo bảng database
    with app.app_context():
        db.create_all()
        
        # Khởi tạo admin views
        from app.admin.views import init_admin_views
        init_admin_views(flask_admin)
    
    return app