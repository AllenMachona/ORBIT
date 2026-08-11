from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.order import Order, OrderItem
from app.models.payment import Payment, PAYMENT_METHODS
from app.utils.payments import get_provider
from app.utils.notify import notify_order

checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')


@checkout_bp.route('/', methods=['GET', 'POST'])
@login_required
def checkout():
    items = current_user.cart_items.all()
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('shop.catalog'))

    subtotal = sum(i.line_total() for i in items)
    deposit_pct = current_app.config['DEPOSIT_PERCENTAGE']
    deposit_due = round(subtotal * deposit_pct, 2)
    balance_due = round(subtotal - deposit_due, 2)

    if request.method == 'POST':
        delivery_method = request.form.get('delivery_method', 'collection')
        campus = request.form.get('campus', current_user.campus or '')
        delivery_address = request.form.get('delivery_address', '').strip()
        payment_method = request.form.get('payment_method', 'mock')
        payer_identifier = request.form.get('payer_identifier', '').strip()

        if delivery_method == 'delivery' and not delivery_address:
            flash('Please provide a delivery address, or choose campus collection instead.', 'danger')
            return render_template('checkout.html', items=items, subtotal=subtotal,
                                    deposit_due=deposit_due, balance_due=balance_due,
                                    payment_methods=PAYMENT_METHODS)

        order = Order(
            user_id=current_user.id,
            total_amount=subtotal, deposit_amount=deposit_due, balance_amount=balance_due,
            delivery_method=delivery_method, campus=campus, delivery_address=delivery_address,
        )
        db.session.add(order)
        db.session.flush()

        for cart_item in items:
            db.session.add(OrderItem(
                order_id=order.id, product_id=cart_item.product_id,
                product_name=f"{cart_item.product.name}",
                condition=cart_item.product.condition,
                unit_price=cart_item.product.price, quantity=cart_item.quantity,
            ))

        provider = get_provider(payment_method if payment_method in PAYMENT_METHODS else None)
        try:
            result = provider.charge(deposit_due, payer_identifier, order.order_number)
        except NotImplementedError as exc:
            db.session.rollback()
            flash(str(exc), 'danger')
            return render_template('checkout.html', items=items, subtotal=subtotal,
                                    deposit_due=deposit_due, balance_due=balance_due,
                                    payment_methods=PAYMENT_METHODS)

        payment = Payment(
            order_id=order.id, payment_type='deposit', method=payment_method,
            amount=deposit_due, status='completed' if result.success else 'failed',
            provider_reference=result.provider_reference, failure_reason=result.failure_reason,
        )
        db.session.add(payment)

        if result.success:
            order.deposit_paid = True
            order.deposit_paid_at = datetime.utcnow()
            order.status = 'deposit_paid'

            for cart_item in items:
                db.session.delete(cart_item)

            db.session.commit()

            notify_order(
                order, f'Order Confirmed — {order.order_number}',
                f"Hi {current_user.first_name}, your order {order.order_number} is confirmed. "
                f"Deposit of P{deposit_due:.2f} received. Your items will take approximately "
                f"{current_app.config['PREORDER_LEAD_DAYS']} working days to arrive — we'll notify you "
                f"the moment they do, so you can settle the balance of P{balance_due:.2f} and collect.",
            )

            flash('Payment successful! Your order is confirmed.', 'success')
            return redirect(url_for('checkout.confirmation', order_id=order.id))
        else:
            order.status = 'cancelled'
            order.cancelled_at = datetime.utcnow()
            order.cancelled_reason = 'Deposit payment failed'
            db.session.commit()
            flash('Payment failed. Please try again or choose a different payment method.', 'danger')
            return render_template('checkout.html', items=items, subtotal=subtotal,
                                    deposit_due=deposit_due, balance_due=balance_due,
                                    payment_methods=PAYMENT_METHODS)

    return render_template('checkout.html', items=items, subtotal=subtotal,
                            deposit_due=deposit_due, balance_due=balance_due,
                            payment_methods=PAYMENT_METHODS)


@checkout_bp.route('/confirmation/<int:order_id>')
@login_required
def confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Order not found.', 'danger')
        return redirect(url_for('shop.home'))
    return render_template('order_confirmation.html', order=order)
