import os
import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

SECURITY_QUESTIONS = [
    "What was the name of your first pet?",
    "What city were you born in?",
    "What is your mother's maiden name?",
    "What was the name of your first school?",
    "What is your favorite childhood movie?",
]

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
    question = f"{a} {op} {b}"
    return question, str(answer)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        q, a = generate_captcha()
        session['captcha_answer'] = a
        session['captcha_question'] = q
        return render_template('auth/register.html',
                               captcha_question=q,
                               security_questions=SECURITY_QUESTIONS)

    username = request.form['username'].strip()
    email = request.form['email'].strip()
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    captcha_input = request.form.get('captcha', '').strip()
    security_question = request.form.get('security_question', '')
    security_answer = request.form.get('security_answer', '').strip().lower()

    # Captcha check
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

    if not security_answer:
        flash('Security answer is required.', 'warning')
        return redirect(url_for('auth.register'))

    user = User(username=username, email=email)
    user.set_password(password)
    user.security_question = security_question
    user.security_answer = generate_password_hash(security_answer)
    db.session.add(user)
    db.session.commit()
    flash('Registration successful! You can now log in.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        q, a = generate_captcha()
        session['captcha_answer'] = a
        session['captcha_question'] = q
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
        user = User.query.filter_by(username=username).first()
        if user and user.security_question:
            session['reset_username'] = username
            return redirect(url_for('auth.reset_password_verify'))
        flash('Username not found or no security question set.', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    return render_template('auth/reset_password_request.html')

@auth_bp.route('/reset_password_verify', methods=['GET', 'POST'])
def reset_password_verify():
    username = session.get('reset_username')
    if not username:
        return redirect(url_for('auth.reset_password_request'))
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('auth.reset_password_request'))

    if request.method == 'POST':
        answer = request.form.get('security_answer', '').strip().lower()
        if check_password_hash(user.security_answer, answer):
            session['reset_verified'] = username
            return redirect(url_for('auth.reset_password'))
        flash('Incorrect answer. Try again.', 'danger')

    return render_template('auth/reset_password_verify.html',
                           question=user.security_question,
                           username=username)

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
        user.set_password(password)
        db.session.commit()
        session.pop('reset_verified', None)
        session.pop('reset_username', None)
        flash('Password updated successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html')
