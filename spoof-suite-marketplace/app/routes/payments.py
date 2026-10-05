from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import Deposit, db
import requests
from datetime import datetime, timedelta

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

@payments_bp.route('/', methods=['GET', 'POST'])
@login_required
def add_funds():
    wallet_balance = current_user.wallet_balance or 0.0
    # Payment methods - BTC and USDT only
    payment_addresses = {
        'USDT_TRC20': "TUjuxkyc12zUbVgWiEQn17VYKf4yB5YYm1",
        'BTC': "35yWsg6WJRfQg7h3sKXnt93r1Dz3WpCSoX"
    }
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        currency = request.form.get('currency')
        tx_hash = request.form.get('tx_hash')
        deposit = Deposit(user_id=current_user.id, amount=amount, currency=currency, tx_hash=tx_hash)
        db.session.add(deposit)
        db.session.commit()
        flash("Deposit submitted! Waiting for blockchain confirmation.", "success")
        return redirect(url_for('payments.add_funds'))
    deposits = Deposit.query.filter_by(user_id=current_user.id).order_by(Deposit.id.desc()).all()
    return render_template(
        'payments.html',
        wallet_balance=wallet_balance,
        payment_addresses=payment_addresses,
        usdt_wallet_address=payment_addresses['USDT_TRC20'],  # Backward compatibility
        btc_wallet_address=payment_addresses['BTC'],  # Backward compatibility
        deposits=deposits
    )

def check_btc_confirmed(tx_hash, min_confirmations=1):
    url = f"https://api.blockchair.com/bitcoin/dashboards/transaction/{tx_hash}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        tx = data['data'][tx_hash]['transaction']
        return tx['confirmations'] >= min_confirmations
    return False

def check_usdt_trc20_confirmed(tx_hash):
    url = f"https://apilist.tronscan.org/api/transaction-info?hash={tx_hash}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return data.get('confirmed', False)
    return False

@payments_bp.route('/confirm_deposits')
@login_required
def confirm_deposits():
    max_pending_time = timedelta(hours=2)
    now = datetime.utcnow()
    deposits = Deposit.query.filter_by(user_id=current_user.id, status='pending').all()
    for dep in deposits:
        confirmed = False
        if dep.currency == 'BTC':
            confirmed = check_btc_confirmed(dep.tx_hash)
        elif dep.currency == 'USDT':
            confirmed = check_usdt_trc20_confirmed(dep.tx_hash)
        if confirmed:
            dep.status = 'confirmed'
            cashback = 0.0
            # Enhanced cashback tiers
            if dep.amount >= 1000:
                cashback = dep.amount * 0.75  # 75% for $1000+
                flash(f"🎉 PLATINUM BONUS! 75% cashback: ${cashback:.2f}", "success")
            elif dep.amount >= 500:
                cashback = dep.amount * 0.60  # 60% for $500+
                flash(f"🥇 GOLD BONUS! 60% cashback: ${cashback:.2f}", "success")
            elif dep.amount >= 300:
                cashback = dep.amount * 0.50  # 50% for $300+
                flash(f"🥈 SILVER BONUS! 50% cashback: ${cashback:.2f}", "info")
            elif dep.amount >= 100:
                cashback = dep.amount * 0.25  # 25% for $100+
                flash(f"🥉 BRONZE BONUS! 25% cashback: ${cashback:.2f}", "info")

            if cashback > 0:
                current_user.wallet_balance += cashback
            current_user.wallet_balance += dep.amount
            db.session.commit()
            flash(f"Deposit of ${dep.amount:.2f} confirmed and added!", "success")
        # Cancel if pending too long
        elif dep.created_at and (now - dep.created_at) > max_pending_time:
            dep.status = 'cancelled'
            db.session.commit()
            flash(f"Deposit with TX {dep.tx_hash} cancelled due to timeout.", "warning")
    return redirect(url_for('payments.add_funds'))