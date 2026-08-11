import secrets
from datetime import datetime
from app.extensions import db

ORDER_STATUSES = ['pending', 'deposit_paid', 'arrived', 'delivered', 'cancelled']
DELIVERY_METHODS = ['collection', 'delivery']


def generate_order_number():
    return f"OT-{datetime.utcnow():%Y%m}-{secrets.token_hex(3).upper()}"


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(30), unique=True, nullable=False, default=generate_order_number)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    status = db.Column(db.String(20), default='pending', index=True)

    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    deposit_amount = db.Column(db.Numeric(10, 2), nullable=False)
    balance_amount = db.Column(db.Numeric(10, 2), nullable=False)

    deposit_paid = db.Column(db.Boolean, default=False)
    deposit_paid_at = db.Column(db.DateTime)
    balance_paid = db.Column(db.Boolean, default=False)
    balance_paid_at = db.Column(db.DateTime)

    delivery_method = db.Column(db.String(20), default='collection')
    campus = db.Column(db.String(100))
    delivery_address = db.Column(db.Text)

    arrived_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancelled_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='order', lazy='dynamic')
    notifications = db.relationship('NotificationLog', backref='order', lazy='dynamic')

    def status_label(self):
        return {
            'pending': 'Pending Deposit',
            'deposit_paid': 'Deposit Paid — Awaiting Arrival',
            'arrived': 'Arrived — Balance Due',
            'delivered': 'Delivered',
            'cancelled': 'Cancelled',
        }.get(self.status, self.status.title())

    def status_step(self):
        order_map = {'pending': 1, 'deposit_paid': 2, 'arrived': 3, 'delivered': 4}
        return order_map.get(self.status, 0)

    def __repr__(self):
        return f'<Order {self.order_number} status={self.status}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

    product_name = db.Column(db.String(200), nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship('Product')

    def line_total(self):
        return round(float(self.unit_price) * self.quantity, 2)

    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'
