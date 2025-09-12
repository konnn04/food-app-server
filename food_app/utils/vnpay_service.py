import hmac
import hashlib
from urllib.parse import urlencode
from datetime import datetime
from flask import current_app


def _hmac_sha512(key: str, data: str) -> str:
    return hmac.new(key.encode('utf-8'), data.encode('utf-8'), hashlib.sha512).hexdigest()


def build_payment_url(txn_ref: str, amount_vnd: float, ip_address: str, order_info: str = 'Deposit', order_type: str = 'other') -> str:
    cfg = current_app.config
    vnp_params = {
        'vnp_Version': '2.1.0',
        'vnp_Command': 'pay',
        'vnp_TmnCode': cfg['VNPAY_TMN_CODE'],
        'vnp_Amount': int(round(amount_vnd * 100)),
        'vnp_CreateDate': datetime.utcnow().strftime('%Y%m%d%H%M%S'),
        'vnp_CurrCode': 'VND',
        'vnp_IpAddr': ip_address or '127.0.0.1',
        'vnp_Locale': 'vn',
        'vnp_OrderInfo': order_info,
        'vnp_OrderType': order_type,
        'vnp_ReturnUrl': cfg['VNPAY_RETURN_URL'],
        'vnp_TxnRef': txn_ref,
    }

    # Sort parameters by key
    sorted_items = sorted(vnp_params.items())
    query_string = urlencode(sorted_items)
    secure_hash = _hmac_sha512(cfg['VNPAY_HASH_SECRET'], query_string)
    return f"{cfg['VNPAY_PAYMENT_URL']}?{query_string}&vnp_SecureHash={secure_hash}"


def verify_ipn(params: dict) -> bool:
    cfg = current_app.config
    params = dict(params)
    secure_hash = params.pop('vnp_SecureHash', None)
    params.pop('vnp_SecureHashType', None)
    sorted_items = sorted(params.items())
    query_string = urlencode(sorted_items)
    calc_hash = _hmac_sha512(cfg['VNPAY_HASH_SECRET'], query_string)
    return secure_hash is not None and secure_hash.lower() == calc_hash.lower()
