from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.order import Order
from app.models.payment import Payment, PAYMENT_METHODS
from app.utils.payments import get_provider
from app.utils.notify import notify_order

account_bp = Blueprint('account', __name__, url_prefix='/account')


@account_bp.route('/orders')
@login_required
def orders():
    my_orders = current_user.orders.order_by(Order.created_at.desc()).all()
    return render_template('account/orders.html', orders=my_orders)


@account_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Order not found.', 'danger')
        return redirect(url_for('account.orders'))
    return render_template('account/order_detail.html', order=order, payment_methods=PAYMENT_METHODS)


@account_bp.route('/orders/<int:order_id>/pay-balance', methods=['POST'])
@login_required
def pay_balance(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Order not found.', 'danger')
        return redirect(url_for('account.orders'))

    if order.status != 'arrived':
        flash('The balance can only be paid once your order has arrived.', 'warning')
        return redirect(url_for('account.order_detail', order_id=order.id))

    if order.balance_paid:
        flash('The balance for this order has already been paid.', 'info')
        return redirect(url_for('account.order_detail', order_id=order.id))

    payment_method = request.form.get('payment_method', 'mock')
    payer_identifier = request.form.get('payer_identifier', '').strip()

    provider = get_provider(payment_method if payment_method in PAYMENT_METHODS else None)
    try:
        result = provider.charge(order.balance_amount, payer_identifier, order.order_number)
    except NotImplementedError as exc:
        flash(str(exc), 'danger')
        return redirect(url_for('account.order_detail', order_id=order.id))

    db.session.add(Payment(
        order_id=order.id, payment_type='balance', method=payment_method,
        amount=order.balance_amount, status='completed' if result.success else 'failed',
        provider_reference=result.provider_reference, failure_reason=result.failure_reason,
    ))

    if result.success:
        order.balance_paid = True
        order.balance_paid_at = datetime.utcnow()
        db.session.commit()

        notify_order(
            order, f'Balance Paid — {order.order_number}',
            f"Thanks {current_user.first_name}! Your balance of P{order.balance_amount:.2f} for "
            f"order {order.order_number} has been received. Please arrange collection/delivery.",
        )
        flash('Balance paid! You can now arrange collection or delivery.', 'success')
    else:
        db.session.commit()
        flash('Balance payment failed. Please try again.', 'danger')

    return redirect(url_for('account.order_detail', order_id=order.id))
