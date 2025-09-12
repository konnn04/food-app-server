from flask import Blueprint, request
from flasgger import swag_from
from food_app.utils.decorators import jwt_customer_required, jwt_required, jwt_base_user_required
from food_app.utils.responses import success_response, error_response
from food_app.utils.vnpay_service import build_payment_url, verify_ipn
from food_app.models import DepositTransaction
from food_app import db
import uuid


payment_bp = Blueprint('payment', __name__)


@payment_bp.route('/deposit/create/', methods=['POST'])
@jwt_base_user_required
@swag_from({'tags': ['Payment'], 'summary': 'Create deposit via VNPay (any user)', 'requestBody': {'required': True, 'content': {'application/json': {'schema': {'type': 'object', 'required': ['amount'], 'properties': {'amount': {'type': 'number'}}}}}}})
def create_deposit(current_base_user):
    try:
        data = request.get_json() or {}
        amount = float(data.get('amount', 0))
        if amount <= 0:
            return error_response('Số tiền không hợp lệ', 400)

        order_id = str(uuid.uuid4()).replace('-', '')[:20]
        txn = DepositTransaction(
            customer_id=current_base_user.id,
            provider='vnpay',
            order_id=order_id,
            amount=amount,
            status='pending',
            raw_request=data
        )
        db.session.add(txn)
        db.session.commit()

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        pay_url = build_payment_url(order_id, amount, ip)
        return success_response('Tạo lệnh nạp tiền thành công', {'payment_url': pay_url, 'order_id': order_id})
    except Exception as e:
        return error_response(f'Lỗi tạo lệnh nạp tiền: {str(e)}', 500)


@payment_bp.route('/vnpay/return/', methods=['GET'])
@swag_from({'tags': ['Payment'], 'summary': 'VNPay return URL (display purpose)'})
def vnpay_return():
    # In sandbox or when IPN cannot reach server, credit as fallback (idempotent)
    params = request.args.to_dict()
    ok = verify_ipn(params)
    data = {'valid_signature': ok, 'params': params}
    try:
        if ok:
            txn_ref = params.get('vnp_TxnRef')
            response_code = params.get('vnp_ResponseCode')
            amount = int(params.get('vnp_Amount', '0')) / 100.0
            if txn_ref and response_code == '00':
                txn = DepositTransaction.query.filter_by(order_id=txn_ref, provider='vnpay').first()
                if txn and txn.status != 'success' and abs(txn.amount - amount) < 1e-6:
                    from food_app.models.customer import Customer
                    from food_app.models.user import User
                    base_user = Customer.query.get(txn.customer_id) or User.query.get(txn.customer_id)
                    if base_user:
                        base_user.balance = (base_user.balance or 0) + txn.amount
                        txn.status = 'success'
                        db.session.commit()
                        data['credited_by_return'] = True
        return success_response('Kết quả thanh toán', data)
    except Exception as e:
        return error_response(f'Lỗi xử lý return: {str(e)}', 500)


@payment_bp.route('/vnpay/ipn/', methods=['GET', 'POST'])
@swag_from({'tags': ['Payment'], 'summary': 'VNPay IPN (server to server)'})
def vnpay_ipn():
    try:
        params = request.values.to_dict()
        if not verify_ipn(params):
            return ({'RspCode': '97', 'Message': 'Invalid signature'}), 200

        txn_ref = params.get('vnp_TxnRef')
        response_code = params.get('vnp_ResponseCode')
        amount = int(params.get('vnp_Amount', '0')) / 100.0

        txn = DepositTransaction.query.filter_by(order_id=txn_ref, provider='vnpay').first()
        if not txn:
            return ({'RspCode': '01', 'Message': 'Order not found'}), 200

        # Idempotent handling
        if txn.status == 'success':
            return ({'RspCode': '00', 'Message': 'Confirm Success'}), 200

        txn.raw_ipn = params
        if response_code == '00' and abs(txn.amount - amount) < 1e-6:
            # Credit balance to base user (Customer or User)
            from food_app.models.customer import Customer
            from food_app.models.user import User
            base_user = Customer.query.get(txn.customer_id) or User.query.get(txn.customer_id)
            if not base_user:
                txn.status = 'failed'
                db.session.commit()
                return ({'RspCode': '02', 'Message': 'User not found'}), 200
            base_user.balance = (base_user.balance or 0) + txn.amount
            txn.status = 'success'
            db.session.commit()
            return ({'RspCode': '00', 'Message': 'Confirm Success'}), 200
        else:
            txn.status = 'failed'
            db.session.commit()
            return ({'RspCode': '00', 'Message': 'Confirm Success'}), 200
    except Exception as e:
        return ({'RspCode': '99', 'Message': f'Unknown error: {str(e)}'}), 200

@payment_bp.route('/wallet/balance/', methods=['GET'])
@jwt_base_user_required
@swag_from({'tags': ['Payment'], 'summary': 'Get wallet balance (any user)'})
def get_wallet_balance(current_base_user):
    return success_response('Số dư ví hiện tại', {'balance': float(current_base_user.balance or 0)})


@payment_bp.route('/order/pay/', methods=['POST'])
@jwt_customer_required
@swag_from({'tags': ['Payment'], 'summary': 'Pay order using wallet then VNPay for remainder', 'requestBody': {'required': True, 'content': {'application/json': {'schema': {'type': 'object', 'required': ['order_id'], 'properties': {'order_id': {'type': 'integer'}}}}}}})
def pay_order(current_customer):
    try:
        data = request.get_json() or {}
        order_id = data.get('order_id')
        if not order_id:
            return error_response('Thiếu order_id', 400)

        from food_app.models.order import Order
        order = Order.query.filter_by(id=order_id, customer_id=current_customer.id).first()
        if not order:
            return error_response('Không tìm thấy đơn hàng', 404)

        amount_due = float(order.total_amount or 0)
        wallet = float(current_customer.balance or 0)

        if wallet >= amount_due:
            # Deduct fully from wallet
            current_customer.balance = wallet - amount_due
            db.session.commit()
            # Mark order as paid
            order.status = 'paid'
            db.session.commit()
            return success_response('Thanh toán bằng số dư thành công', {'paid_by_wallet': amount_due, 'order_status': order.status})
        else:
            # Deduct what we can? Business says if không đủ -> tạo VNPay mới, không trừ phần thiếu
            # So keep wallet unchanged and create VNPay for full amount_due (or remainder). Here we choose remainder.
            remainder = amount_due - wallet if wallet > 0 else amount_due
            order_ref = str(uuid.uuid4()).replace('-', '')[:20]
            txn = DepositTransaction(
                customer_id=current_customer.id,
                provider='vnpay',
                order_id=order_ref,
                amount=remainder,
                status='pending',
                raw_request={'type': 'order_payment', 'order_id': order.id}
            )
            db.session.add(txn)
            db.session.commit()

            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            pay_url = build_payment_url(order_ref, remainder, ip, order_info=f'Pay order {order.id}')
            return success_response('Số dư không đủ, chuyển VNPay', {
                'payment_url': pay_url,
                'order_id': order.id,
                'amount_wallet': 0,
                'amount_vnpay': remainder
            })
    except Exception as e:
        return error_response(f'Lỗi thanh toán: {str(e)}', 500)


