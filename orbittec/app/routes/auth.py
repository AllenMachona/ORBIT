from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User, CAMPUS_CHOICES

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('shop.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'danger')
            return render_template('auth/register.html', campuses=CAMPUS_CHOICES)

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/register.html', campuses=CAMPUS_CHOICES)

        user = User(
            email=email, first_name=request.form.get('first_name', '').strip(),
            last_name=request.form.get('last_name', '').strip(),
            phone=request.form.get('phone', '').strip(),
            campus=request.form.get('campus', ''),
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Welcome to {user.campus or "OrbitTec"}! Your account has been created.', 'success')
        return redirect(url_for('shop.home'))

    return render_template('auth/register.html', campuses=CAMPUS_CHOICES)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        next_url = request.form.get('next') or url_for('shop.home')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', next=next_url)

        if not user.is_active:
            flash('This account has been deactivated.', 'danger')
            return render_template('auth/login.html', next=next_url)

        login_user(user)
        flash(f'Welcome back, {user.first_name}!', 'success')
        return redirect(next_url)

    return render_template('auth/login.html', next=request.args.get('next', ''))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('shop.home'))
