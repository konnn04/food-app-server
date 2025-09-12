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
    
    # Cấu hình JWT
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'
    app.config['JWT_CLAIMS_IN_REFRESH_TOKEN'] = True
    
    db.init_app(app)
    # CORS: allow FE origins explicitly; wildcard with credentials is blocked by browsers
    allowed_origins = [
        'https://www.konnn04.live',
        'https://konnn04.live',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'https://food.riikonteam.io.vn'
    ]
    CORS(
        app,
        resources={r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"]
        }}
    )
    jwt.init_app(app)
    login_manager.init_app(app)
    # Admin login endpoint is AdminAuthView.default_view = 'index'
    login_manager.login_view = 'admin_auth.index'
    flask_admin.init_app(app)
    swagger.init_app(app)
    
    # Global JSON error handlers
    from werkzeug.exceptions import HTTPException
    from food_app.utils.responses import error_response

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        return error_response(e.description or 'HTTP Error', e.code or 500)

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        return error_response('Internal Server Error', 500)

    # Đăng ký blueprints
    from food_app.routes.auth import auth_bp
    from food_app.routes.search import search_bp
    from food_app.routes.customer import customer_bp
    from food_app.routes.staff import staff_bp
    from food_app.routes.admin_api import admin_api_bp
    from food_app.routes.category import category_bp
    from food_app.routes.food import food_bp
    from food_app.routes.restaurant import restaurant_bp
    from food_app.routes.coupon import coupon_bp
    from food_app.routes.payment import payment_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(customer_bp, url_prefix='/api/customer')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(admin_api_bp, url_prefix='/api/admin')
    app.register_blueprint(category_bp, url_prefix='/api/category')
    app.register_blueprint(food_bp, url_prefix='/api/food')
    app.register_blueprint(restaurant_bp, url_prefix='/api/restaurant')
    app.register_blueprint(coupon_bp, url_prefix='/api/coupon')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')
    
    from food_app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        
        from food_app.admin.views import init_admin_views
        init_admin_views(flask_admin)
    
    return app