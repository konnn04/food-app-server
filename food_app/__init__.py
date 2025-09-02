from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_admin import Admin
from flask_login import LoginManager
from flasgger import Swagger
from config import config

db = SQLAlchemy()
jwt = JWTManager()
login_manager = LoginManager()
flask_admin = Admin(name='Food Ordering Admin', template_mode='bootstrap4')
swagger = Swagger()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    CORS(app, origins=["*"], supports_credentials=True)
    jwt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_auth.login'
    flask_admin.init_app(app)
    swagger.init_app(app)
    
    # Đăng ký blueprints
    from food_app.routes.auth import auth_bp
    from food_app.routes.food import food_bp
    from food_app.routes.order import order_bp
    from food_app.routes.review import review_bp
    from food_app.routes.cart import cart_bp
    from food_app.routes.coupon import coupon_bp
    from food_app.routes.invoice import invoice_bp
    from food_app.routes.admin_api import admin_api_bp
    from food_app.routes.restaurant import restaurant_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(food_bp, url_prefix='/api/food')
    app.register_blueprint(order_bp, url_prefix='/api/order')
    app.register_blueprint(review_bp, url_prefix='/api/review')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(coupon_bp, url_prefix='/api/coupon')
    app.register_blueprint(invoice_bp, url_prefix='/api/invoice')
    app.register_blueprint(admin_api_bp, url_prefix='/api/admin')
    app.register_blueprint(restaurant_bp, url_prefix='/api/restaurant')
    from food_app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        
        from food_app.admin.views import init_admin_views
        init_admin_views(flask_admin)
    
    return app