from food_app import db
from datetime import datetime


class DepositTransaction(db.Model):
    __tablename__ = 'deposit_transactions'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    provider = db.Column(db.String(20), nullable=False)  # 'vnpay' | 'momo'
    order_id = db.Column(db.String(64), unique=True, nullable=False)  # vnp_TxnRef, momo orderId
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending | success | failed
    raw_request = db.Column(db.JSON)
    raw_ipn = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'provider': self.provider,
            'order_id': self.order_id,
            'amount': self.amount,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


