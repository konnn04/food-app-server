from flask import Blueprint, request
from food_app.controllers.admin_controller import AdminController
from food_app.utils.decorators import admin_required
from flask_jwt_extended import jwt_required
from flasgger import swag_from

admin_api_bp = Blueprint('admin_api', __name__)

@admin_api_bp.route('/dashboard/', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({'tags': ['Admin'], 'summary': 'Dashboard stats'})
def get_dashboard_data():
    """API lấy dữ liệu tổng quan cho dashboard"""
    return AdminController.get_dashboard_data()

@admin_api_bp.route('/users/', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({'tags': ['Admin'], 'summary': 'List users'})
def get_users():
    """API lấy danh sách người dùng"""
    role = request.args.get('role')
    return AdminController.get_users(role)

@admin_api_bp.route('/customers/', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({'tags': ['Admin'], 'summary': 'List customers'})
def get_customers():
    """API lấy danh sách khách hàng"""
    return AdminController.get_customers()

@admin_api_bp.route('/orders/', methods=['GET'])
@jwt_required()
@admin_required
@swag_from({'tags': ['Admin'], 'summary': 'List all orders'})
def get_all_orders():
    """API lấy tất cả đơn hàng"""
    status = request.args.get('status')
    return AdminController.get_all_orders(status)
