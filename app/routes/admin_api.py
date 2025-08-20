from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.customer import Customer
from app.models.restaurant import Restaurant
from app.models.food import Food
from app.models.order import Order
from app.utils.responses import success_response, error_response
from app.utils.jwt_service import get_user_id_from_jwt, get_role_from_jwt
from flask_jwt_extended import jwt_required
from app.utils.decorators import admin_required

admin_api_bp = Blueprint('admin_api', __name__)

@admin_api_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def get_dashboard_data():
    """API lấy dữ liệu tổng quan cho dashboard"""
    try:
        total_customers = Customer.query.count()
        total_orders = Order.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
        
        # Tính doanh thu hôm nay
        from datetime import datetime, time
        today = datetime.now().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)
        today_orders = Order.query.filter(Order.created_at.between(today_start, today_end))
        today_revenue = today_orders.with_entities(db.func.sum(Order.total_amount)).scalar() or 0
        today_order_count = today_orders.count()
        
        # Thống kê đơn hàng theo trạng thái
        status_counts = {}
        for status in ['pending', 'confirmed', 'preparing', 'delivered', 'cancelled']:
            status_counts[status] = Order.query.filter_by(status=status).count()
        
        data = {
            'customers': {
                'total': total_customers,
                'new_today': Customer.query.filter(Customer.created_at.between(today_start, today_end)).count()
            },
            'orders': {
                'total': total_orders,
                'today': today_order_count,
                'status_counts': status_counts
            },
            'revenue': {
                'total': float(total_revenue),
                'today': float(today_revenue)
            }
        }
        
        return success_response('Lấy dữ liệu dashboard thành công', data)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@admin_api_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """API lấy danh sách người dùng"""
    try:
        role = request.args.get('role')
        
        if role:
            users = User.query.filter_by(role=role).all()
        else:
            users = User.query.all()
        
        users_data = [user.to_dict() for user in users]
        
        return success_response('Lấy danh sách người dùng thành công', users_data)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@admin_api_bp.route('/customers', methods=['GET'])
@jwt_required()
@admin_required
def get_customers():
    """API lấy danh sách khách hàng"""
    try:
        customers = Customer.query.all()
        customers_data = [customer.to_dict() for customer in customers]
        
        return success_response('Lấy danh sách khách hàng thành công', customers_data)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@admin_api_bp.route('/orders', methods=['GET'])
@jwt_required()
@admin_required
def get_all_orders():
    """API lấy tất cả đơn hàng"""
    try:
        status = request.args.get('status')
        
        query = Order.query
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).all()
        orders_data = [order.to_dict() for order in orders]
        
        return success_response('Lấy danh sách đơn hàng thành công', orders_data)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)
