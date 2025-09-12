import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///food_ordering.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Config
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Flask Admin
    FLASK_ADMIN_SWATCH = 'cerulean'
    
    # Pagination Config
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 10
    MAX_PER_PAGE = 100
    MIN_PER_PAGE = 1
    
    # Search Config
    MAX_SEARCH_RESULTS = 50
    MAX_FOODS_PER_RESTAURANT = 3
    
    # Order Config
    ORDER_STATUSES = ['pending', 'accepted', 'completed', 'cancelled']
    DEFAULT_ORDER_STATUS = 'pending'
    
    # User Roles
    USER_ROLES = ['customer', 'staff', 'manager', 'owner', 'admin']
    DEFAULT_USER_ROLE = 'customer'
    
    # File Upload Config
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Distance Config (km)
    MAX_DELIVERY_DISTANCE = 20.0
    
    # Rating Config
    MIN_RATING = 1
    MAX_RATING = 5

    # VNPay Settings
    VNPAY_TMN_CODE = os.getenv('VNPAY_TMN_CODE', '')
    VNPAY_HASH_SECRET = os.getenv('VNPAY_HASH_SECRET', '')
    VNPAY_PAYMENT_URL = os.getenv('VNPAY_PAYMENT_URL', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html')
    VNPAY_RETURN_URL = os.getenv('VNPAY_RETURN_URL', 'http://localhost:5000/api/payment/vnpay/return/')
    VNPAY_IPN_URL = os.getenv('VNPAY_IPN_URL', 'http://localhost:5000/api/payment/vnpay/ipn/')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}