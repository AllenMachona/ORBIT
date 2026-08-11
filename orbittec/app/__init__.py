import os
from flask import Flask
from app.extensions import db, login_manager, migrate
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['INSTANCE_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app import models  # noqa: F401
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.shop import shop_bp
    from app.routes.cart import cart_bp
    from app.routes.checkout import checkout_bp
    from app.routes.account import account_bp
    from app.routes.admin import admin_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        from flask_login import current_user
        cart_count = 0
        if current_user.is_authenticated:
            cart_count = sum(i.quantity for i in current_user.cart_items)
        return {
            'now': datetime.utcnow(),
            'company_name': app.config['COMPANY_NAME'],
            'company_tagline': app.config['COMPANY_TAGLINE'],
            'cart_count': cart_count,
        }

    return app
