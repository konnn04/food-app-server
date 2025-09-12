from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from food_app.controllers.auth_controller import AuthController
from food_app.dao import UserDAO, CustomerDAO
from flasgger import swag_from
from food_app.utils.jwt_service import get_user_id_from_jwt, get_user_type_from_jwt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/staff/login/', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Staff/admin login',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'password': {'type': 'string'}
                    },
                    'required': ['username', 'password']
                }
            }
        }
    },
    'responses': {
        '200': {'description': 'Success'},
        '401': {'description': 'Invalid credentials'}
    }
})
def staff_login():
    data = request.get_json()
    return AuthController.staff_login(data)

@auth_bp.route('/staff/register/', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Create owner account',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'password': {'type': 'string'},
                        'full_name': {'type': 'string'},
                        'email': {'type': 'string'},
                        'phone': {'type': 'string'}
                    },
                    'required': ['username', 'password', 'full_name']
                }
            }
        }
    },
    'responses': {
        '201': {'description': 'Created'},
        '400': {'description': 'Bad request'}
    }
})
def create_owner():
    data = request.get_json()
    return AuthController.create_owner(data)

@auth_bp.route('/profile/', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_user_id_from_jwt()
    user_type = get_user_type_from_jwt()

    if user_type == 'customer':
        user = CustomerDAO.get_customer_by_id(user_id)
    else:  
        user = UserDAO.get_user_by_id(user_id)

    return AuthController.get_profile(user)

@auth_bp.route('/profile/', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_user_id_from_jwt()
    user_type = get_user_type_from_jwt()
    data = request.get_json()

    if user_type == 'customer':
        user = CustomerDAO.get_customer_by_id(user_id)
    else: 
        user = UserDAO.get_user_by_id(user_id)

    return AuthController.update_profile(user, data)

@auth_bp.route('/customer/send-otp/', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Send OTP to customer phone',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'phone': {'type': 'string'}
                    },
                    'required': ['phone']
                }
            }
        }
    },
    'responses': {
        '200': {'description': 'OTP sent'},
        '400': {'description': 'Bad request'}
    }
})
def send_customer_otp():
    data = request.get_json()
    return AuthController.send_customer_otp(data)

@auth_bp.route('/customer/verify-otp/', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Verify customer OTP and login',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'phone': {'type': 'string'},
                        'otp': {'type': 'string'}
                    },
                    'required': ['phone', 'otp']
                }
            }
        }
    },
    'responses': {
        '200': {'description': 'Login successful'},
        '400': {'description': 'Invalid OTP'}
    }
})
def verify_customer_otp():
    data = request.get_json()
    return AuthController.verify_customer_otp(data)

@auth_bp.route('/refresh/', methods=['POST'])
@jwt_required(refresh=True)
@swag_from({
    'tags': ['Auth'],
    'summary': 'Refresh access token',
    'responses': {
        '200': {'description': 'Token refreshed'},
        '401': {'description': 'Invalid refresh token'}
    }
})
def refresh_token():
    identity = get_jwt_identity()
    return AuthController.refresh_token(identity)