from datetime import datetime
from app.extensions import db

PAYMENT_TYPES = ['deposit', 'balance']
PAYMENT_METHODS = ['orange_money', 'mascom_myzaka', 'card', 'mock']
PAYMENT_STATUSES = ['pending', 'completed', 'failed']


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    payment_type = db.Column(db.String(20), nullable=False)
    method = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')

    provider_reference = db.Column(db.String(120))
    failure_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Payment {self.payment_type} {self.amount} status={self.status}>'
