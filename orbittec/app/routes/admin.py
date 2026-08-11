import os
import secrets
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.order import Order, ORDER_STATUSES
from app.models.product import Product, Category, CONDITION_CHOICES
from app.utils.notify import notify_order

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    status_filter = request.args.get('status', '')
    query = Order.query
    if status_filter in ORDER_STATUSES:
        query = query.filter_by(status=status_filter)
    orders = query.order_by(Order.created_at.desc()).all()

    counts = {s: Order.query.filter_by(status=s).count() for s in ORDER_STATUSES}
    total_revenue_collected = sum(
        float(o.deposit_amount) + (float(o.balance_amount) if o.balance_paid else 0)
        for o in Order.query.all()
    )

    return render_template(
        'admin/dashboard.html', orders=orders, counts=counts,
        status_filter=status_filter, statuses=ORDER_STATUSES,
        total_revenue_collected=total_revenue_collected,
    )


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/mark-arrived', methods=['POST'])
@login_required
@admin_required
def mark_arrived(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'deposit_paid':
        flash(f'Order must be in "Deposit Paid" status to mark as arrived (currently: {order.status_label()}).', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order.id))

    order.status = 'arrived'
    order.arrived_at = datetime.utcnow()
    db.session.commit()

    notify_order(
        order, f'Your Order Has Arrived! — {order.order_number}',
        f"Great news {order.customer.first_name}! Your order {order.order_number} has arrived in Botswana. "
        f"Please pay the remaining balance of P{order.balance_amount:.2f} and arrange your "
        f"{'collection at ' + (order.campus or 'campus') if order.delivery_method == 'collection' else 'delivery'}.",
        channels=('email', 'sms'),
    )

    flash(f'Order {order.order_number} marked as arrived. Customer notified.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))


@admin_bp.route('/orders/<int:order_id>/mark-delivered', methods=['POST'])
@login_required
@admin_required
def mark_delivered(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'arrived' or not order.balance_paid:
        flash('Order must be "Arrived" with balance paid before it can be marked delivered.', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order.id))

    order.status = 'delivered'
    order.delivered_at = datetime.utcnow()
    db.session.commit()

    notify_order(
        order, f'Order Delivered — {order.order_number}',
        f"Your order {order.order_number} has been marked as delivered/collected. Thanks for shopping with "
        f"{current_app.config['COMPANY_NAME']}!",
    )

    flash(f'Order {order.order_number} marked as delivered.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))


@admin_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('A cancellation reason is required.', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order.id))

    order.status = 'cancelled'
    order.cancelled_at = datetime.utcnow()
    order.cancelled_reason = reason
    db.session.commit()

    notify_order(order, f'Order Cancelled — {order.order_number}', f"Your order {order.order_number} has been cancelled. Reason: {reason}")
    flash(f'Order {order.order_number} cancelled.', 'info')
    return redirect(url_for('admin.order_detail', order_id=order.id))


@admin_bp.route('/products')
@login_required
@admin_required
def products():
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=all_products)


@admin_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
@admin_required
def product_new():
    categories = Category.query.all()

    if request.method == 'POST':
        product = Product()
        _apply_product_form(product)
        db.session.add(product)
        db.session.commit()
        flash(f'{product.name} added.', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', product=None, categories=categories, conditions=CONDITION_CHOICES)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()

    if request.method == 'POST':
        _apply_product_form(product)
        db.session.commit()
        flash(f'{product.name} updated.', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', product=product, categories=categories, conditions=CONDITION_CHOICES)


@admin_bp.route('/products/<int:product_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def product_toggle_active(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = not product.is_active
    db.session.commit()
    flash(f'{product.name} is now {"active" if product.is_active else "hidden"}.', 'success')
    return redirect(url_for('admin.products'))


def _apply_product_form(product):
    product.category_id = request.form.get('category_id', type=int)
    product.name = request.form.get('name', '').strip()
    product.brand = request.form.get('brand', '').strip()
    product.condition = request.form.get('condition', 'new')
    product.description = request.form.get('description', '').strip()
    product.specs = request.form.get('specs', '').strip()
    product.price = request.form.get('price', 0, type=float)
    product.stock_quantity = request.form.get('stock_quantity', 0, type=int)
    product.is_preorder = bool(request.form.get('is_preorder'))
    product.is_trending = bool(request.form.get('is_trending'))
    product.is_active = bool(request.form.get('is_active'))

    image = request.files.get('image')
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1].lower()
        if ext in ALLOWED_IMAGE_EXTENSIONS:
            filename = secure_filename(f"{secrets.token_hex(6)}{ext}")
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            product.image_path = filename
        else:
            flash(f'Image type {ext} not allowed — use PNG, JPG, or WEBP.', 'warning')
