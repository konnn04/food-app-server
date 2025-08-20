from flask import Blueprint, request, jsonify
from app import db
from app.models.order import Order, OrderItem
from app.models.food import Food
from app.models.customer import Customer
from app.utils.responses import success_response, error_response

order_bp = Blueprint('order', __name__)

@order_bp.route('/', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('customer_id') or not data.get('items'):
            return error_response('Thiếu thông tin đặt hàng', 400)
        
        # Kiểm tra customer tồn tại
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return error_response('Khách hàng không tồn tại', 404)
        
        # Tạo order
        order = Order(
            customer_id=data['customer_id'],
            delivery_address=data.get('delivery_address'),
            delivery_phone=data.get('delivery_phone', customer.phone),
            notes=data.get('notes'),
            total_amount=0
        )
        
        total_amount = 0
        restaurant_id = None
        
        # Thêm order items
        for item_data in data['items']:
            food = Food.query.get(item_data.get('food_id'))
            if not food or not food.available:
                return error_response(f'Món ăn ID {item_data.get("food_id")} không có sẵn', 400)
            
            # Kiểm tra tất cả món ăn phải cùng nhà hàng
            if restaurant_id is None:
                restaurant_id = food.restaurant_id
            elif restaurant_id != food.restaurant_id:
                return error_response('Tất cả món ăn phải cùng một nhà hàng', 400)
            
            quantity = int(item_data.get('quantity', 1))
            price = food.price
            
            order_item = OrderItem(
                food_id=food.id,
                quantity=quantity,
                price=price
            )
            order.order_items.append(order_item)
            total_amount += quantity * price
        
        order.total_amount = total_amount
        order.restaurant_id = restaurant_id
        
        # Cập nhật thống kê customer
        customer.total_orders += 1
        customer.loyalty_points += int(total_amount / 1000)  # 1 điểm per 1000 VND
        
        db.session.add(order)
        db.session.commit()
        
        return success_response('Đặt hàng thành công', order.to_dict(), 201)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@order_bp.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer_orders(customer_id):
    try:
        orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
        orders_data = [order.to_dict() for order in orders]
        
        return success_response('Lấy danh sách đơn hàng thành công', orders_data)
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)

@order_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'confirmed', 'preparing', 'delivered', 'cancelled']:
            return error_response('Trạng thái không hợp lệ', 400)
        
        order = Order.query.get(order_id)
        if not order:
            return error_response('Không tìm thấy đơn hàng', 404)
        
        order.status = new_status
        db.session.commit()
        
        return success_response('Cập nhật trạng thái thành công', order.to_dict())
    
    except Exception as e:
        return error_response(f'Lỗi server: {str(e)}', 500)