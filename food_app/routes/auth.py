from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from food_app.controllers.auth_controller import AuthController
from food_app.dao import UserDAO, CustomerDAO
from food_app.utils.decorators import require_role
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/staff/login', methods=['POST'])
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

@auth_bp.route('/staff/register', methods=['POST'])
def create_owner():
    data = request.get_json()
    return AuthController.create_owner(data)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    user_type = identity.get('user_type')
    user_id = identity.get('user_id')

    if user_type == 'customer':
        user = CustomerDAO.get_customer_by_id(user_id)
    else:  
        user = UserDAO.get_user_by_id(user_id)

    return AuthController.get_profile(user)

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    identity = get_jwt_identity()
    user_type = identity.get('user_type')
    user_id = identity.get('user_id')
    data = request.get_json()

    if user_type == 'customer':
        user = CustomerDAO.get_customer_by_id(user_id)
    else: 
        user = UserDAO.get_user_by_id(user_id)

    return AuthController.update_profile(user, data)

@auth_bp.route('/customer/send-otp', methods=['POST'])
def send_customer_otp():
    data = request.get_json()
    return AuthController.send_customer_otp(data)

@auth_bp.route('/customer/verify-otp', methods=['POST'])
def verify_customer_otp():
    data = request.get_json()
    return AuthController.verify_customer_otp(data)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    return AuthController.refresh_token(identity)