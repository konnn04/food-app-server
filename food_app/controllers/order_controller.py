from food_app.dao import OrderDAO, CustomerDAO
from food_app.utils.responses import success_response, error_response

class OrderController:
    @staticmethod
    def create_order(data):
        """Tạo đơn hàng mới"""
        try:
            # Validation
            if not data.get('customer_id') or not data.get('items'):
                return error_response('Thiếu thông tin đặt hàng', 400)

            # Kiểm tra customer tồn tại
            customer = CustomerDAO.get_customer_by_id(data['customer_id'])
            if not customer:
                return error_response('Khách hàng không tồn tại', 404)

            # Xác định restaurant từ món đầu tiên
            if not data['items']:
                return error_response('Không có món trong đơn hàng', 400)
            from food_app.models.food import Food
            first_food = Food.query.get(data['items'][0]['food_id'])
            if not first_food:
                return error_response('Món ăn không tồn tại', 400)
            restaurant_id = first_food.restaurant_id

            # Chuẩn bị dữ liệu order
            order_data = {
                'customer_id': data['customer_id'],
                'restaurant_id': restaurant_id,
                'delivery_address': data.get('delivery_address'),
                'delivery_phone': data.get('delivery_phone', customer.phone),
                'notes': data.get('notes')
            }

            # Tạo order với items
            order = OrderDAO.create_order(order_data, data['items'])

            # Cập nhật thống kê customer
            CustomerDAO.update_customer(customer, {
                'total_orders': customer.total_orders + 1,
                'loyalty_points': customer.loyalty_points + int(order.total_amount / 1000)  # 1 điểm per 1000 VND
            })

            return success_response('Đặt hàng thành công', order.to_dict(), 201)

        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_customer_orders(customer_id):
        """Lấy danh sách đơn hàng của khách hàng"""
        try:
            orders = OrderDAO.get_orders_by_customer(customer_id)
            orders_data = [order.to_dict() for order in orders]

            return success_response('Lấy danh sách đơn hàng thành công', orders_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_order(order_id):
        """Lấy thông tin một đơn hàng"""
        try:
            order = OrderDAO.get_order_by_id(order_id)

            if not order:
                return error_response('Không tìm thấy đơn hàng', 404)

            return success_response('Lấy thông tin đơn hàng thành công', order.to_dict())

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def update_order_status(order_id, new_status):
        """Cập nhật trạng thái đơn hàng"""
        try:
            if new_status not in ['pending', 'confirmed', 'preparing', 'ready', 'delivering', 'delivered', 'cancelled']:
                return error_response('Trạng thái không hợp lệ', 400)

            order = OrderDAO.get_order_by_id(order_id)
            if not order:
                return error_response('Không tìm thấy đơn hàng', 404)

            updated_order = OrderDAO.update_order_status(order, new_status)

            return success_response('Cập nhật trạng thái thành công', updated_order.to_dict())

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_restaurant_orders(restaurant_id):
        """Lấy danh sách đơn hàng của nhà hàng"""
        try:
            orders = OrderDAO.get_orders_by_restaurant(restaurant_id)
            orders_data = [order.to_dict() for order in orders]

            return success_response('Lấy danh sách đơn hàng thành công', orders_data)

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def cancel_order(order_id, data):
        try:
            order = OrderDAO.get_order_by_id(order_id)
            if not order:
                return error_response('Không tìm thấy đơn hàng', 404)
            cancel_reason_id = data.get('cancel_reason_id')
            cancel_note = data.get('cancel_note')
            order = OrderDAO.cancel_order(order, cancel_reason_id, cancel_note)
            return success_response('Huỷ đơn thành công', order.to_dict())
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def assign_staff_to_order(order_id, staff_id):
        """Gán nhân viên xử lý đơn hàng"""
        try:
            from food_app.dao import UserDAO

            order = OrderDAO.get_order_by_id(order_id)
            if not order:
                return error_response('Không tìm thấy đơn hàng', 404)

            staff = UserDAO.get_user_by_id(staff_id)
            if not staff:
                return error_response('Không tìm thấy nhân viên', 404)

            if staff.role not in ['staff', 'manager']:
                return error_response('Người dùng không phải là nhân viên', 400)

            # Kiểm tra staff thuộc nhà hàng của order (1 user - 1 restaurant or owner)
            if staff.role in ['staff', 'manager']:
                if staff.restaurant_id != order.restaurant_id:
                    return error_response('Nhân viên không thuộc nhà hàng này', 400)
            elif staff.role == 'owner':
                if not (staff.owned_restaurant and staff.owned_restaurant.id == order.restaurant_id):
                    return error_response('Chủ quán không sở hữu nhà hàng này', 400)

            OrderDAO.update_order_status(order, {'assigned_staff_id': staff_id})

            return success_response('Gán nhân viên thành công', order.to_dict())

        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)
