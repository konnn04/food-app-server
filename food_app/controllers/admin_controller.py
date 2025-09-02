from food_app.dao import UserDAO, CustomerDAO, OrderDAO
from food_app.utils.responses import success_response, error_response

class AdminController:
    @staticmethod
    def get_dashboard_data():
        """API lấy dữ liệu tổng quan cho dashboard"""
        try:
            total_customers = CustomerDAO.get_all_customers()
            total_orders = OrderDAO.get_all_orders()
            total_revenue = OrderDAO.get_total_revenue()

            # Tính doanh thu hôm nay
            today_revenue = OrderDAO.get_today_revenue()
            today_orders = OrderDAO.get_today_orders()
            today_order_count = today_orders.count()

            # Thống kê đơn hàng theo trạng thái
            status_counts = OrderDAO.get_orders_status_counts()

            # Thống kê khách hàng mới hôm nay
            new_customers_today = CustomerDAO.get_new_customers_today()

            data = {
                'customers': {
                    'total': len(total_customers),
                    'new_today': new_customers_today
                },
                'orders': {
                    'total': len(total_orders),
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

    @staticmethod
    def get_users(role=None):
        """API lấy danh sách người dùng"""
        try:
            users = UserDAO.get_users_by_role(role)
            users_data = [user.to_dict() for user in users]

            return success_response('Lấy danh sách người dùng thành công', users_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_customers():
        """API lấy danh sách khách hàng"""
        try:
            customers = CustomerDAO.get_all_customers()
            customers_data = [customer.to_dict() for customer in customers]

            return success_response('Lấy danh sách khách hàng thành công', customers_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_all_orders(status=None):
        """API lấy tất cả đơn hàng"""
        try:
            orders = OrderDAO.get_orders_by_status(status)
            orders_data = [order.to_dict() for order in orders]

            return success_response('Lấy danh sách đơn hàng thành công', orders_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)
