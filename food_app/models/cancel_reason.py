from food_app import db
from datetime import datetime

class CancelReason(db.Model):
    __tablename__ = 'cancel_reasons'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


