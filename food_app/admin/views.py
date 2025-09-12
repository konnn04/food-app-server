from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask import redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user
from food_app import db
from food_app.models.user import User
from food_app.models.customer import Customer
from food_app.models.food import Food
from food_app.models.order import Order
from food_app.models.order_item import OrderItem
from food_app.models.order_item_topping import OrderItemTopping
from food_app.models.restaurant import Restaurant
from food_app.models.category import Category
from food_app.models.topping import Topping
from food_app.models.review import Review
from food_app.models.coupon import Coupon
from food_app.models.invoice import Invoice
from food_app.models.cart import Cart, CartItem
from markupsafe import Markup
from sqlalchemy import func

class AdminRequiredMixin:
    def is_accessible(self):
        return bool(getattr(current_user, 'is_authenticated', False)) and getattr(current_user, 'role', None) == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_auth.index', next=request.url))

class AdminAuthView(BaseView):
    default_view = 'index'
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        from food_app.models.user import User
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            next_url = request.args.get('next') or url_for('admin_index.index')
            user = User.query.filter((User.username == username) | (User.email == username)).first()
            if user and user.role == 'admin' and user.check_password(password):
                login_user(user)
                return redirect(next_url)
            flash('Đăng nhập thất bại. Vui lòng kiểm tra thông tin.', 'danger')
        return self.render('admin/login.html')

    @expose('/logout')
    def logout(self):
        logout_user()
        return redirect(url_for('admin_auth.index'))

class BaseSafeModelView(AdminRequiredMixin, ModelView):
    def handle_view_exception(self, exc):
        flash(str(exc), 'danger')
        return redirect(url_for('admin_index.index'))

class UserModelView(BaseSafeModelView):
    column_list = ('id', 'username', 'email', 'phone', 'first_name', 'last_name', 'role', 'is_active', 'restaurant_id')
    column_searchable_list = ('username', 'email', 'phone', 'first_name', 'last_name')
    column_filters = ()
    form_excluded_columns = ('password_hash',)

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.set_password('password123')

class CustomerModelView(BaseSafeModelView):
    column_list = ('id', 'phone', 'first_name', 'last_name', 'email', 'loyalty_points', 'total_orders', 'is_active')
    column_searchable_list = ('phone', 'first_name', 'last_name', 'email')
    column_filters = ('is_active',)
    form_excluded_columns = ('firebase_uid', 'otp_code', 'otp_expires_at', 'otp_attempts')

class RestaurantModelView(BaseSafeModelView):
    column_list = ('id', 'name', 'address', 'phone', 'email', 'tax_code', 'approval_status', 'owner', 'is_active')
    column_searchable_list = ('name', 'address', 'phone', 'email', 'tax_code')
    column_filters = ('is_active', 'approval_status', 'owner.first_name', 'owner.last_name')
    column_sortable_list = ('id', 'name', 'created_at', 'approval_date')
    
    form_excluded_columns = ('created_at', 'approval_date')
    
    def _approval_status_formatter(view, context, model, name):
        status_colors = {
            'pending': 'warning',
            'approved': 'success', 
            'rejected': 'danger'
        }
        color = status_colors.get(model.approval_status, 'secondary')
        return Markup(f'<span class="badge badge-{color}">{model.approval_status}</span>')
    
    column_formatters = {
        'approval_status': _approval_status_formatter
    }

class FoodModelView(BaseSafeModelView):
    column_list = ('id', 'name', 'price', 'categories', 'available', 'restaurant.name')
    column_searchable_list = ('name', 'categories.name', 'restaurant.name')
    column_filters = ('available', 'categories.name', 'restaurant.name')
    form_columns = ('name', 'description', 'price', 'categories', 'toppings', 'image_url', 'available', 'restaurant')

class OrderModelView(BaseSafeModelView):
    column_list = ('id', 'customer.full_name', 'restaurant.name', 'total_amount', 'status', 'created_at')
    column_filters = ('status', 'created_at')
    column_default_sort = ('created_at', True) 
    
class CategoryModelView(BaseSafeModelView):
    column_list = ('id', 'name', 'description', 'created_at')
    column_searchable_list = ('name',)

class ToppingModelView(BaseSafeModelView):
    column_list = ('id', 'name', 'price', 'is_available')
    column_searchable_list = ('name',)
    column_filters = ('is_available',)

class ReviewModelView(BaseSafeModelView):
    can_create = False
    can_edit = False
    column_list = ('id', 'customer_id', 'restaurant_id', 'food_id', 'rating', 'comment', 'created_at')
    column_filters = ('restaurant_id', 'food_id', 'rating')

class CouponModelView(BaseSafeModelView):
    column_list = ('id', 'code', 'discount_type', 'discount_value', 'restaurant_id', 'is_active', 'start_date', 'end_date')
    column_filters = ('discount_type', 'is_active', 'restaurant_id')
    form_columns = ('code', 'description', 'discount_type', 'discount_value', 'start_date', 'end_date', 'min_order_amount', 'max_discount_amount', 'is_active', 'restaurant', 'foods')

class InvoiceModelView(BaseSafeModelView):
    can_create = False
    column_list = ('id', 'order_id', 'payment_method', 'third_party_name', 'third_party_code', 'subtotal', 'tax', 'total', 'created_at')
    column_filters = ('payment_method', 'third_party_name', 'created_at')

class CartModelView(BaseSafeModelView):
    can_create = False
    can_edit = False
    column_list = ('id', 'customer_id', 'restaurant_id', 'updated_at')

class CartItemModelView(BaseSafeModelView):
    can_create = False
    can_edit = False
    column_list = ('id', 'cart_id', 'food_id', 'quantity', 'price')

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
        
        # Doanh thu theo ngày 7 ngày gần nhất
        last_7_days = db.session.query(
            func.date(Order.created_at).label('day'),
            func.coalesce(func.sum(Order.total_amount), 0).label('revenue'),
            func.count(Order.id).label('orders')
        ).group_by(func.date(Order.created_at))
        last_7_days = last_7_days.order_by(func.date(Order.created_at).desc()).limit(7).all()
        daily_labels = [str(r.day) for r in reversed(last_7_days)]
        daily_revenue = [float(r.revenue) for r in reversed(last_7_days)]
        daily_orders = [int(r.orders) for r in reversed(last_7_days)]

        # Doanh thu theo tuần (8 tuần gần nhất)
        # ISO week: year-week
        week_q = db.session.query(
            func.strftime('%Y-%W', Order.created_at).label('week'),
            func.coalesce(func.sum(Order.total_amount), 0).label('revenue')
        ).group_by(func.strftime('%Y-%W', Order.created_at)).order_by(func.strftime('%Y-%W', Order.created_at).desc()).limit(8).all()
        weekly_labels = [r.week for r in reversed(week_q)]
        weekly_revenue = [float(r.revenue) for r in reversed(week_q)]

        # Top 5 món ăn theo doanh thu
        top_foods_q = db.session.query(
            Food.name,
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.price), 0).label('revenue')
        ).join(OrderItem, OrderItem.food_id == Food.id)
        top_foods_q = top_foods_q.group_by(Food.id).order_by(func.sum(OrderItem.quantity * OrderItem.price).desc()).limit(5).all()
        top_food_labels = [r[0] for r in top_foods_q]
        top_food_revenue = [float(r[1]) for r in top_foods_q]

        # Top 5 nhà hàng theo doanh thu
        top_rest_q = db.session.query(
            Restaurant.name,
            func.coalesce(func.sum(Order.total_amount), 0).label('revenue')
        ).join(Order, Order.restaurant_id == Restaurant.id).group_by(Restaurant.id)
        top_rest_q = top_rest_q.order_by(func.sum(Order.total_amount).desc()).limit(5).all()
        top_rest_labels = [r[0] for r in top_rest_q]
        top_rest_revenue = [float(r[1]) for r in top_rest_q]
        
        return self.render('admin/dashboard.html',
                           total_customers=total_customers,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           today_revenue=today_revenue,
                           today_order_count=today_order_count,
                           daily_labels=daily_labels,
                           daily_revenue=daily_revenue,
                           daily_orders=daily_orders,
                           weekly_labels=weekly_labels,
                           weekly_revenue=weekly_revenue,
                           top_food_labels=top_food_labels,
                           top_food_revenue=top_food_revenue,
                           top_rest_labels=top_rest_labels,
                           top_rest_revenue=top_rest_revenue)

def init_admin_views(admin_instance): 
    admin_instance.add_view(AdminAuthView(name='Đăng nhập', endpoint='admin_auth'))
    admin_instance.add_view(DashboardView(name='Dashboard', endpoint='admin_index'))
    admin_instance.add_view(UserModelView(User, db.session, name='Nhân viên', endpoint='admin_users'))
    admin_instance.add_view(CustomerModelView(Customer, db.session, name='Khách hàng', endpoint='admin_customers'))
    admin_instance.add_view(RestaurantModelView(Restaurant, db.session, name='Nhà hàng', endpoint='admin_restaurants'))
    admin_instance.add_view(CategoryModelView(Category, db.session, name='Loại món', endpoint='admin_categories'))
    admin_instance.add_view(FoodModelView(Food, db.session, name='Món ăn', endpoint='admin_foods'))
    admin_instance.add_view(ToppingModelView(Topping, db.session, name='Topping', endpoint='admin_toppings'))
    admin_instance.add_view(OrderModelView(Order, db.session, name='Đơn hàng', endpoint='admin_orders'))
    admin_instance.add_view(ReviewModelView(Review, db.session, name='Đánh giá', endpoint='admin_reviews'))
    admin_instance.add_view(CouponModelView(Coupon, db.session, name='Mã giảm giá', endpoint='admin_coupons'))
    admin_instance.add_view(InvoiceModelView(Invoice, db.session, name='Hoá đơn', endpoint='admin_invoices'))
    admin_instance.add_view(CartModelView(Cart, db.session, name='Giỏ hàng', endpoint='admin_carts'))
    admin_instance.add_view(CartItemModelView(CartItem, db.session, name='Mục giỏ hàng', endpoint='admin_cart_items'))
