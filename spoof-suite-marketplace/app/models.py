from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import inspect
from . import db  # Use the db from app/__init__.py


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    wallet_balance = db.Column(db.Float, default=0.0)
    btc_wallet_address = db.Column(db.String(128))      # Add this line
    usdt_wallet_address = db.Column(db.String(128))     # Add this line

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    tx_hash = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(32))  # 'credit', 'debit', 'plaid', 'fullz'
    data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)


class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Allow null for marketplace cards
    card_number = db.Column(db.String(20), nullable=False, unique=True)  # Make unique
    card_type = db.Column(db.String(10), nullable=False)  # 'credit' or 'debit'
    category = db.Column(db.String(32))  # 'platinum', 'gold', etc.
    bank = db.Column(db.String(64))
    country = db.Column(db.String(32))
    state = db.Column(db.String(32))  # Add state
    city = db.Column(db.String(64))   # Add city
    zip_code = db.Column(db.String(10))  # Add zip
    address = db.Column(db.String(200))  # Add address
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Card details
    cvv = db.Column(db.String(4))
    expiry = db.Column(db.String(7))  # Format: MM/YY
    holder_name = db.Column(db.String(64))
    price = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)

    # Additional fields for marketplace
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    email_pass = db.Column(db.String(50))
    ssn = db.Column(db.String(15))
    dob = db.Column(db.String(12))
    is_verified = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)  # For marketplace availability

    # Enhanced fields for realism
    bin_code = db.Column(db.String(6))  # First 6 digits
    brand = db.Column(db.String(20))  # visa, mastercard
    level = db.Column(db.String(30))  # Traditional, Gold, Platinum, etc.
    prepaid = db.Column(db.String(5), default="no")  # yes/no
    country_flag = db.Column(db.String(10))  # Flag emoji
    note = db.Column(db.String(50), default="not checked")  # verified/not checked
    validity_percent = db.Column(db.Integer)  # 80, 60, 55 for unverified cards

    user = db.relationship('User', backref='credit_cards')

    def __repr__(self):
        return f'<CreditCard {self.card_number} - {self.card_type}>'

    def to_dict(self):
        """Convert card to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'card_number': self.card_number,
            'holder_name': self.holder_name,
            'expiry': self.expiry,
            'cvv': self.cvv,
            'card_type': self.card_type,
            'category': self.category,
            'bank': self.bank,
            'country': self.country,
            'state': self.state,
            'city': self.city,
            'zip_code': self.zip_code,
            'address': self.address,
            'balance': self.balance,
            'price': self.price,
            'phone': self.phone,
            'email': self.email,
            'email_pass': self.email_pass,
            'ssn': self.ssn,
            'dob': self.dob,
            'is_verified': self.is_verified,
            'is_available': self.is_available
        }


def get_user_profile(user_id):
    """Get user profile information"""
    user = User.query.get(user_id)
    if user:
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.username.title(),  # Simple full name from username
            'wallet_balance': user.wallet_balance or 0.0,
            'btc_wallet_address': user.btc_wallet_address,
            'usdt_wallet_address': user.usdt_wallet_address
        }
    return None


class Cart(db.Model):
    """Cart model for storing user's cart items"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('credit_card.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='cart_items')
    card = db.relationship('CreditCard', backref='cart_items')

    def __repr__(self):
        return f'<Cart {self.user_id} - {self.card_id}>'


class Purchase(db.Model):
    """Purchase model for tracking user purchases"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('credit_card.id'), nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='purchases')
    card = db.relationship('CreditCard', backref='purchases')

    def __repr__(self):
        return f'<Purchase {self.user_id} - {self.card_id}>'


def get_cart(user_id):
    """Get user's cart items"""
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    return [{'card': item.card, 'quantity': item.quantity} for item in cart_items]


def clear_cart(user_id):
    """Clear user's cart"""
    Cart.query.filter_by(user_id=user_id).delete()
    db.session.commit()


def give_cards_to_user(user, cart_items):
    """Process purchase - move cards from cart to purchases"""
    total_cost = 0
    for item in cart_items:
        card = item.card
        purchase = Purchase(
            user_id=user.id,
            card_id=card.id,
            purchase_price=card.price
        )
        db.session.add(purchase)
        total_cost += card.price

        # Mark card as unavailable
        card.is_available = False

    # Deduct from user's wallet
    user.wallet_balance -= total_cost

    # Clear cart
    clear_cart(user.id)

    db.session.commit()
    return total_cost
