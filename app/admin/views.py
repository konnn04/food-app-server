from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask import redirect, url_for, request, flash
from flask_login import current_user, login_required
from app import db
from app.models.user import User
from app.models.customer import Customer
from app.models.food import Food
from app.models.order import Order, OrderItem
from app.models.restaurant import Restaurant

class AdminRequiredMixin:
    def is_accessible(self):
        # Trong môi trường thực tế, đây sẽ kiểm tra quyền admin
        # Ví dụ đơn giản, bạn có thể mở rộng thêm với Flask-Login
        return True
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.login_view'))

class UserModelView(AdminRequiredMixin, ModelView):
    column_list = ('id', 'username', 'email', 'phone', 'full_name', 'role', 'is_active')
    column_searchable_list = ('username', 'email', 'phone', 'full_name')
    column_filters = ('role', 'is_active')
    form_excluded_columns = ('password_hash', 'firebase_uid')
    
    def on_model_change(self, form, model, is_created):
        # Xử lý logic khi tạo/sửa user
        if is_created:
            # Đặt mật khẩu mặc định khi tạo mới
            model.set_password('password123')

class CustomerModelView(AdminRequiredMixin, ModelView):
    column_list = ('id', 'phone', 'full_name', 'email', 'loyalty_points', 'total_orders', 'is_active')
    column_searchable_list = ('phone', 'full_name', 'email')
    column_filters = ('is_active',)
    form_excluded_columns = ('firebase_uid', 'otp_code', 'otp_expires_at', 'otp_attempts')

class RestaurantModelView(AdminRequiredMixin, ModelView):
    column_list = ('id', 'name', 'address', 'phone', 'email', 'is_active')
    column_searchable_list = ('name', 'address', 'phone', 'email')
    column_filters = ('is_active',)

class FoodModelView(AdminRequiredMixin, ModelView):
    column_list = ('id', 'name', 'price', 'category', 'available', 'restaurant.name')
    column_searchable_list = ('name', 'category')
    column_filters = ('available', 'category', 'restaurant.name')

class OrderModelView(AdminRequiredMixin, ModelView):
    column_list = ('id', 'customer.full_name', 'restaurant.name', 'total_amount', 'status', 'created_at')
    column_filters = ('status', 'created_at')
    column_default_sort = ('created_at', True)  # Sắp xếp theo ngày tạo mới nhất

class DashboardView(AdminRequiredMixin, BaseView):
    @expose('/')
    def index(self):
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
        
        return self.render('admin/dashboard.html',
                           total_customers=total_customers,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           today_revenue=today_revenue,
                           today_order_count=today_order_count)

def init_admin_views(admin_instance):  # Rename parameter to avoid confusion
    # Add views with unique endpoint names
    admin_instance.add_view(DashboardView(name='Dashboard', endpoint='admin_dashboard'))
    admin_instance.add_view(UserModelView(User, db.session, name='Nhân viên', endpoint='admin_users'))
    admin_instance.add_view(CustomerModelView(Customer, db.session, name='Khách hàng', endpoint='admin_customers'))
    admin_instance.add_view(RestaurantModelView(Restaurant, db.session, name='Nhà hàng', endpoint='admin_restaurants'))
    admin_instance.add_view(FoodModelView(Food, db.session, name='Món ăn', endpoint='admin_foods'))
    admin_instance.add_view(OrderModelView(Order, db.session, name='Đơn hàng', endpoint='admin_orders'))
