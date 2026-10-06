import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import get_config

mail = Mail()
db = SQLAlchemy()

def create_app(config_name=None):
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_class = get_config()
    else:
        from .config import config
        config_class = config.get(config_name, config['default'])

    app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        from . import models
        from .models import FireSale

    migrate = Migrate(app, db)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.payments import payments_bp
    from app.routes.credit_cards import cards_bp
    from app.routes.cart import cart_bp
    from app.routes.help import help_bp
    from app.routes.bin_checker import bin_checker_bp
    from app.routes.plaid_logs import plaid_bp
    from app.routes.fullz import fullz_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(bin_checker_bp)
    app.register_blueprint(plaid_bp)
    app.register_blueprint(fullz_bp)
    return app