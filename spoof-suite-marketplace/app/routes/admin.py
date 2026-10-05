from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, User, Deposit, Purchase, CreditCard, Notification

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    users = User.query.order_by(User.id.desc()).all()
    deposits = Deposit.query.order_by(Deposit.created_at.desc()).limit(50).all()
    purchases = Purchase.query.order_by(Purchase.purchased_at.desc()).limit(50).all()
    pending_deposits = Deposit.query.filter_by(status='pending').count()
    total_users = User.query.count()
    total_cards = CreditCard.query.count()
    return render_template('admin/dashboard.html',
                           users=users,
                           deposits=deposits,
                           purchases=purchases,
                           pending_deposits=pending_deposits,
                           total_users=total_users,
                           total_cards=total_cards)

@admin_bp.route('/deposit/<int:deposit_id>/approve', methods=['POST'])
@login_required
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
@login_required
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
@login_required
@admin_required
def adjust_balance(user_id):
    user = User.query.get_or_404(user_id)
    amount = float(request.form.get('amount', 0))
    user.wallet_balance = (user.wallet_balance or 0) + amount
    db.session.commit()
    flash(f'Balance adjusted by ${amount:.2f} for {user.username}.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.dashboard'))
    user = User.query.get_or_404(user_id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User {username} deleted.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/make_admin', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin access {status} for {user.username}.', 'success')
    return redirect(url_for('admin.dashboard'))
