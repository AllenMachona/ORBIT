from datetime import datetime
from app.extensions import db

CATEGORY_CHOICES = ['phones', 'laptops', 'accessories']
CONDITION_CHOICES = ['new', 'refurbished']


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    """New and Refurbished units of the "same model" are deliberately
    separate rows (not one row with two prices) — that's what the brief
    asks for and it keeps each listing's condition/price/stock independent
    and clearly labeled, matching the trust requirement."""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100))
    condition = db.Column(db.String(20), nullable=False, default='new')
    description = db.Column(db.Text)
    specs = db.Column(db.Text)

    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_path = db.Column(db.String(300))

    is_preorder = db.Column(db.Boolean, default=True)
    stock_quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_trending = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def deposit_amount(self):
        from flask import current_app
        pct = current_app.config['DEPOSIT_PERCENTAGE']
        return round(float(self.price) * pct, 2)

    def condition_label(self):
        return 'Brand New' if self.condition == 'new' else 'Good Quality Refurbished'

    def __repr__(self):
        return f'<Product {self.name} ({self.condition})>'
