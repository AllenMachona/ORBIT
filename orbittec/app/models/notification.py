from datetime import datetime
from app.extensions import db


class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    channel = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    delivered = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<NotificationLog {self.channel} order={self.order_id}>'
