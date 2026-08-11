from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.cart import CartItem
from app.models.product import Product

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


@cart_bp.route('/')
@login_required
def view():
    items = current_user.cart_items.all()
    subtotal = sum(i.line_total() for i in items)
    return render_template('cart.html', items=items, subtotal=subtotal)


@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add(product_id):
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()
    quantity = max(1, request.form.get('quantity', 1, type=int))

    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        db.session.add(CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity))
    db.session.commit()

    flash(f'{product.name} ({product.condition_label()}) added to cart.', 'success')
    return redirect(request.referrer or url_for('shop.catalog'))


@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('You cannot modify another user\'s cart.', 'danger')
        return redirect(url_for('cart.view'))

    quantity = request.form.get('quantity', 1, type=int)
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    return redirect(url_for('cart.view'))


@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('You cannot modify another user\'s cart.', 'danger')
        return redirect(url_for('cart.view'))

    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view'))
