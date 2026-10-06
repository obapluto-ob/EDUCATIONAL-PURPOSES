import os
import random
import secrets
import string
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def generate_captcha():
    a = random.randint(2, 15)
    b = random.randint(1, 10)
    op = random.choice(['+', '-', '*'])
    if op == '+':
        answer = a + b
    elif op == '-':
        answer = a - b
    else:
        answer = a * b
    return f"{a} {op} {b}", str(answer)


def make_recovery_key():
    """Generate a human-readable recovery key like SWSS-A3F9-KX72-PL01"""
    chars = string.ascii_uppercase + string.digits
    parts = [''.join(random.choices(chars, k=4)) for _ in range(4)]
    return '-'.join(parts)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        q, a = generate_captcha()
        session['captcha_answer'] = a
        return render_template('auth/register.html', captcha_question=q)

    username = request.form['username'].strip()
    email = request.form['email'].strip()
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    captcha_input = request.form.get('captcha', '').strip()

    if captcha_input != session.get('captcha_answer', ''):
        flash('Captcha incorrect. Please try again.', 'warning')
        return redirect(url_for('auth.register'))

    if password != confirm_password:
        flash('Passwords do not match.', 'warning')
        return redirect(url_for('auth.register'))

    if User.query.filter_by(username=username).first():
        flash('Username already taken.', 'warning')
        return redirect(url_for('auth.register'))

    if User.query.filter_by(email=email).first():
        flash('Email already registered.', 'warning')
        return redirect(url_for('auth.register'))

    recovery_key = make_recovery_key()
    user = User(username=username, email=email)
    user.set_password(password)
    user.recovery_key_hash = generate_password_hash(recovery_key)
    db.session.add(user)
    db.session.commit()

    # Show recovery key once — store in session to display on next page
    session['show_recovery_key'] = recovery_key
    session['recovery_username'] = username
    return redirect(url_for('auth.show_recovery_key'))


@auth_bp.route('/recovery-key')
def show_recovery_key():
    key = session.pop('show_recovery_key', None)
    username = session.pop('recovery_username', None)
    if not key:
        return redirect(url_for('auth.login'))
    return render_template('auth/recovery_key.html', recovery_key=key, username=username)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        q, a = generate_captcha()
        session['captcha_answer'] = a
        return render_template('auth/login.html', captcha_question=q)

    captcha_input = request.form.get('captcha', '').strip()
    if captcha_input != session.get('captcha_answer', ''):
        flash('Captcha incorrect. Please try again.', 'warning')
        return redirect(url_for('auth.login'))

    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for('main.index'))
    flash('Invalid username or password.', 'danger')
    return redirect(url_for('auth.login'))


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
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        recovery_key = request.form.get('recovery_key', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and user.recovery_key_hash and check_password_hash(user.recovery_key_hash, recovery_key):
            session['reset_verified'] = username
            return redirect(url_for('auth.reset_password'))
        flash('Invalid username or recovery key.', 'danger')
    return render_template('auth/reset_password_request.html')


@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    username = session.get('reset_verified')
    if not username:
        return redirect(url_for('auth.reset_password_request'))
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('auth.reset_password_request'))

    if request.method == 'POST':
        password = request.form['password']
        confirm = request.form.get('confirm_password', '')
        if password != confirm:
            flash('Passwords do not match.', 'warning')
            return redirect(url_for('auth.reset_password'))
        # Generate new recovery key on password reset
        new_key = make_recovery_key()
        user.set_password(password)
        user.recovery_key_hash = generate_password_hash(new_key)
        db.session.commit()
        session.pop('reset_verified', None)
        session['show_recovery_key'] = new_key
        session['recovery_username'] = username
        flash('Password updated! Save your new recovery key.', 'success')
        return redirect(url_for('auth.show_recovery_key'))
    return render_template('auth/reset_password.html')


# ── Admin login via SECRET_KEY ──────────────────────────────────────────────

@auth_bp.route('/admin-access', methods=['GET', 'POST'])
def admin_access():
    if session.get('is_admin'):
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        key = request.form.get('key', '').strip()
        if key == current_app.config.get('SECRET_KEY'):
            session['is_admin'] = True
            session.permanent = True
            return redirect(url_for('admin.dashboard'))
        flash('Invalid access key.', 'danger')
    return render_template('auth/admin_access.html')


@auth_bp.route('/admin-logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('auth.login'))
