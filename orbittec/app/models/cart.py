from datetime import datetime
from app.extensions import db


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')

    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='uq_user_product_cart'),)

    def line_total(self):
        return round(float(self.product.price) * self.quantity, 2)

    def __repr__(self):
        return f'<CartItem product={self.product_id} qty={self.quantity}>'
