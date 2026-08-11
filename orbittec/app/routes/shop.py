from flask import Blueprint, render_template, request
from app.models.product import Product, Category

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/')
def home():
    trending = Product.query.filter_by(is_active=True, is_trending=True).limit(8).all()
    if not trending:
        trending = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()

    categories = Category.query.all()
    return render_template('home.html', trending=trending, categories=categories)


@shop_bp.route('/shop')
def catalog():
    category_slug = request.args.get('category', '')
    condition = request.args.get('condition', '')
    search = request.args.get('q', '').strip()

    query = Product.query.filter_by(is_active=True)

    if category_slug:
        query = query.join(Category).filter(Category.slug == category_slug)
    if condition in ('new', 'refurbished'):
        query = query.filter(Product.condition == condition)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    products = query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()

    return render_template(
        'shop.html', products=products, categories=categories,
        selected_category=category_slug, selected_condition=condition, search=search,
    )


@shop_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()
    related = Product.query.filter(
        Product.category_id == product.category_id, Product.id != product.id, Product.is_active.is_(True)
    ).limit(4).all()
    return render_template('product_detail.html', product=product, related=related)
