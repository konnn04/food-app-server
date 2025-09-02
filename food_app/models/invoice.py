from food_app import db
from datetime import datetime

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # cash, card, momo, zalopay, vnpay
    third_party_code = db.Column(db.String(120), nullable=True)
    third_party_name = db.Column(db.String(50), nullable=True)
    subtotal = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('Order', backref='invoice')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'payment_method': self.payment_method,
            'third_party_code': self.third_party_code,
            'third_party_name': self.third_party_name,
            'subtotal': self.subtotal,
            'tax': self.tax,
            'total': self.total,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


