from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models import db, User, Deposit, Purchase, CreditCard, Notification, FireSale
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('auth.admin_access'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@admin_required
def dashboard():
    users = User.query.order_by(User.id.desc()).all()
    deposits = Deposit.query.order_by(Deposit.created_at.desc()).limit(50).all()
    purchases = Purchase.query.order_by(Purchase.purchased_at.desc()).limit(50).all()
    pending_deposits = Deposit.query.filter_by(status='pending').count()
    total_users = User.query.count()
    total_cards = CreditCard.query.count()
    active_sale = FireSale.query.filter_by(is_active=True).first()
    return render_template('admin/dashboard.html',
                           users=users,
                           deposits=deposits,
                           purchases=purchases,
                           pending_deposits=pending_deposits,
                           total_users=total_users,
                           total_cards=total_cards,
                           active_sale=active_sale)

@admin_bp.route('/deposit/<int:deposit_id>/approve', methods=['POST'])
@admin_required
def approve_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    if deposit.status == 'pending':
        deposit.status = 'confirmed'
        user = User.query.get(deposit.user_id)
        if user:
            user.wallet_balance = (user.wallet_balance or 0) + deposit.amount
            notif = Notification(user_id=user.id,
                                 message=f'Your deposit of ${deposit.amount:.2f} has been approved.')
            db.session.add(notif)
        db.session.commit()
        flash(f'Deposit #{deposit_id} approved.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/deposit/<int:deposit_id>/reject', methods=['POST'])
@admin_required
def reject_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    if deposit.status == 'pending':
        deposit.status = 'rejected'
        user = User.query.get(deposit.user_id)
        if user:
            notif = Notification(user_id=user.id,
                                 message=f'Your deposit of ${deposit.amount:.2f} was rejected.')
            db.session.add(notif)
        db.session.commit()
        flash(f'Deposit #{deposit_id} rejected.', 'warning')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/balance', methods=['POST'])
@admin_required
def adjust_balance(user_id):
    user = User.query.get_or_404(user_id)
    amount = float(request.form.get('amount', 0))
    user.wallet_balance = (user.wallet_balance or 0) + amount
    db.session.commit()
    flash(f'Balance adjusted by ${amount:.2f} for {user.username}.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User {username} deleted.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/firesale/start', methods=['POST'])
@admin_required
def start_firesale():
    # Stop any existing active sale first
    FireSale.query.filter_by(is_active=True).update({'is_active': False})
    discount = int(request.form.get('discount', 30))
    duration = int(request.form.get('duration', 10))
    sale = FireSale(discount_percent=discount, duration_minutes=duration, started_at=datetime.utcnow(), is_active=True)
    db.session.add(sale)
    db.session.commit()
    flash(f'🔥 Fire Sale started! {discount}% off for {duration} minutes.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/firesale/stop', methods=['POST'])
@admin_required
def stop_firesale():
    FireSale.query.filter_by(is_active=True).update({'is_active': False})
    db.session.commit()
    flash('Fire Sale stopped.', 'success')
    return redirect(url_for('admin.dashboard'))
