import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app.models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Serializer for tokens - use app's secret key
def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'warning')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/back_to_dashboard')
@login_required
def back_to_dashboard():
    return redirect(url_for('main.index'))

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    from app import mail  # Import mail inside the function to avoid circular import
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            s = get_serializer()
            token = s.dumps(email, salt='password-reset-salt')
            link = url_for('auth.reset_password', token=token, _external=True)
            msg = Message('Password Reset', recipients=[email])
            msg.body = f"""
Hello,

You requested a password reset for your SWSSMILITARIESZONE account.
Click the link below to reset your password:

{link}

If you did not request this, please ignore this email.
"""
            print("Sending email to:", email)  # <-- Add this line
            mail.send(msg)                    # <-- Add this line
            flash('Check your email for a reset link.')
        else:
            flash('Email not found.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        s = get_serializer()
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        flash('The reset link is invalid or has expired.')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)  # implement set_password method
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html')

