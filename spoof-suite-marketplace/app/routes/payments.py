from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app.models import Deposit, db, FireSale
import requests
from datetime import datetime, timedelta

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

MAX_DAILY_DEPOSIT = 5000.0   # max total deposits per user per day
MIN_DEPOSIT = 1.0            # absolute minimum
MAX_SINGLE_DEPOSIT = 2000.0  # max single deposit

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
        try:
            amount = float(request.form.get('amount', 0))
        except (ValueError, TypeError):
            flash('Invalid amount.', 'danger')
            return redirect(url_for('payments.add_funds'))

        # Fraud protection checks
        if amount < MIN_DEPOSIT:
            flash(f'Minimum deposit is ${MIN_DEPOSIT:.2f}.', 'danger')
            return redirect(url_for('payments.add_funds'))
        if amount > MAX_SINGLE_DEPOSIT:
            flash(f'Maximum single deposit is ${MAX_SINGLE_DEPOSIT:.2f}.', 'danger')
            return redirect(url_for('payments.add_funds'))

        # Daily limit check
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_total = db.session.query(db.func.sum(Deposit.amount)).filter(
            Deposit.user_id == current_user.id,
            Deposit.created_at >= today_start,
            Deposit.status != 'rejected'
        ).scalar() or 0.0
        if daily_total + amount > MAX_DAILY_DEPOSIT:
            flash(f'Daily deposit limit of ${MAX_DAILY_DEPOSIT:.2f} reached.', 'danger')
            return redirect(url_for('payments.add_funds'))

        currency = request.form.get('currency')
        tx_hash = request.form.get('tx_hash', '').strip()

        if not tx_hash or len(tx_hash) < 20:
            flash('Invalid transaction hash.', 'danger')
            return redirect(url_for('payments.add_funds'))

        # Duplicate TX hash check — prevent reuse
        if Deposit.query.filter_by(tx_hash=tx_hash).first():
            flash('This transaction hash has already been submitted.', 'danger')
            return redirect(url_for('payments.add_funds'))

        deposit = Deposit(user_id=current_user.id, amount=amount, currency=currency, tx_hash=tx_hash)
        db.session.add(deposit)
        db.session.commit()
        flash('Deposit submitted! It will be verified against the blockchain.', 'success')
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
    try:
        url = f"https://api.blockchair.com/bitcoin/dashboards/transaction/{tx_hash}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            tx = data['data'][tx_hash]['transaction']
            confirmed = tx['confirmations'] >= min_confirmations
            # Return (confirmed, actual_usd_value) — blockchair gives output in satoshis
            # We return None for amount since BTC/USD conversion needs extra call
            return confirmed, None
    except Exception:
        pass
    return False, None


def check_usdt_trc20_confirmed(tx_hash):
    try:
        url = f"https://apilist.tronscan.org/api/transaction-info?hash={tx_hash}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            confirmed = data.get('confirmed', False)
            # Try to get actual USDT amount from token transfers
            actual_amount = None
            transfers = data.get('tokenTransferInfo', {})
            if transfers and transfers.get('symbol') == 'USDT':
                try:
                    actual_amount = float(transfers.get('amount_str', 0)) / 1e6
                except Exception:
                    pass
            return confirmed, actual_amount
    except Exception:
        pass
    return False, None

@payments_bp.route('/confirm_deposits')
@login_required
def confirm_deposits():
    max_pending_time = timedelta(hours=2)
    now = datetime.utcnow()
    deposits = Deposit.query.filter_by(user_id=current_user.id, status='pending').all()
    for dep in deposits:
        confirmed = False
        actual_amount = None
        if dep.currency == 'BTC':
            confirmed, actual_amount = check_btc_confirmed(dep.tx_hash)
        elif dep.currency == 'USDT':
            confirmed, actual_amount = check_usdt_trc20_confirmed(dep.tx_hash)

        if confirmed:
            dep.status = 'confirmed'

            # Fraud: if we got actual on-chain amount, credit that — not what user claimed
            # If actual_amount is None (BTC, no conversion), trust claimed amount for now
            credit_amount = actual_amount if actual_amount is not None else dep.amount

            # If user claimed more than what was actually sent, flag it
            if actual_amount is not None and actual_amount < dep.amount * 0.95:
                dep.status = 'flagged'
                dep.amount = actual_amount  # correct the record
                db.session.commit()
                flash(f'⚠️ Deposit flagged: claimed ${dep.amount:.2f} but only ${actual_amount:.2f} received.', 'danger')
                continue

            cashback = 0.0
            if credit_amount >= 1000:
                cashback = credit_amount * 0.75
                flash(f'🎉 PLATINUM BONUS! 75% cashback: ${cashback:.2f}', 'success')
            elif credit_amount >= 500:
                cashback = credit_amount * 0.60
                flash(f'🥇 GOLD BONUS! 60% cashback: ${cashback:.2f}', 'success')
            elif credit_amount >= 300:
                cashback = credit_amount * 0.50
                flash(f'🥈 SILVER BONUS! 50% cashback: ${cashback:.2f}', 'info')
            elif credit_amount >= 100:
                cashback = credit_amount * 0.25
                flash(f'🥉 BRONZE BONUS! 25% cashback: ${cashback:.2f}', 'info')

            current_user.wallet_balance = (current_user.wallet_balance or 0) + credit_amount + cashback
            db.session.commit()
            flash(f'Deposit of ${credit_amount:.2f} confirmed and added to your wallet!', 'success')

        elif dep.created_at and (now - dep.created_at) > max_pending_time:
            dep.status = 'cancelled'
            db.session.commit()
            flash(f'Deposit TX {dep.tx_hash[:16]}... cancelled — not confirmed within 2 hours.', 'warning')

    return redirect(url_for('payments.add_funds'))


@payments_bp.route('/firesale/status')
def firesale_status():
    sale = FireSale.query.filter_by(is_active=True).first()
    if not sale or sale.seconds_remaining <= 0:
        if sale:
            sale.is_active = False
            db.session.commit()
        return jsonify({'active': False})
    return jsonify({
        'active': True,
        'discount': sale.discount_percent,
        'seconds_remaining': sale.seconds_remaining,
        'ends_at': sale.ends_at.isoformat()
    })