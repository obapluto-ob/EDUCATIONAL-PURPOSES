from flask import Blueprint, session, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
@login_required
def view_cart():
    cart = session.get('cart', [])
    from app.models import CreditCard
    cart_items = []

    for item in cart:
        if 'card_number' not in item or 'card_type' not in item:
            continue
        card = CreditCard.query.filter_by(card_number=item['card_number']).first()
        if card:
            cart_items.append({
                'card_number': card.card_number,
                'card_type': card.card_type or '',
                'country': card.country or '',
                'bank': card.bank or '',
                'quantity': item.get('quantity', 1),
                'price': item.get('price', card.price or 0.0)
            })

    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total_amount=total_amount)

@cart_bp.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    from app.models import CreditCard
    card_number = request.form.get('card_number')
    card_type = request.form.get('card_type')
    quantity = int(request.form.get('quantity', 1))
    next_url = request.form.get('next') or url_for('cart.view_cart')

    if not card_number or not card_type:
        flash('Card number and type are required.', 'danger')
        return redirect(url_for('cart.view_cart'))

    # Get card from database
    card = CreditCard.query.filter_by(card_number=card_number).first()
    if not card:
        flash('Card not found.', 'danger')
        return redirect(url_for('cart.view_cart'))

    cart = session.get('cart', [])
    for item in cart:
        if item.get('card_number') == card_number and item.get('card_type', '').lower() == card_type.lower():
            item['quantity'] += quantity
            break
    else:
        cart.append({
            'card_number': card_number,
            'card_type': card_type,
            'quantity': quantity,
            'price': card.price or 0.0
        })
    session['cart'] = cart
    session.modified = True  # Force session save
    flash('Card added to cart!', 'success')
    return redirect(next_url)

@cart_bp.route('/remove', methods=['POST'])
@login_required
def remove_from_cart():
    card_number = request.form.get('card_number')
    card_type = request.form.get('card_type')
    cart = session.get('cart', [])
    cart = [
        item for item in cart
        if not (item.get('card_number') == card_number and item.get('card_type', '').lower() == card_type.lower())
    ]
    session['cart'] = cart
    session.modified = True  # Force session save
    flash('Card removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', [])
    if not cart:
        flash('Your cart is empty!', 'danger')
        return redirect(url_for('cart.view_cart'))

    from app.models import CreditCard, Purchase, db

    # Calculate total and validate cart items
    total = 0
    valid_items = []

    for item in cart:
        card = CreditCard.query.filter_by(card_number=item.get('card_number')).first()
        if card:
            item_total = item.get('price', card.price or 0.0) * item.get('quantity', 1)
            total += item_total
            valid_items.append({'card': card, 'quantity': item.get('quantity', 1), 'price': item.get('price', card.price or 0.0)})

    if not valid_items:
        flash('No valid items in cart!', 'danger')
        return redirect(url_for('cart.view_cart'))

    wallet_balance = current_user.wallet_balance if current_user.wallet_balance is not None else 0.0

    # Check if user has enough funds
    if wallet_balance < total:
        flash(f'Insufficient funds! You need ${total:.2f} but only have ${wallet_balance:.2f}. Please add funds to complete your purchase.', 'danger')
        return redirect(url_for('payments.add_funds'))

    # User has enough funds - complete the purchase automatically
    try:
        # Deduct from wallet
        current_user.wallet_balance = wallet_balance - total

        # Create purchase records
        for item in valid_items:
            for _ in range(item['quantity']):
                purchase = Purchase(
                    user_id=current_user.id,
                    card_id=item['card'].id,
                    purchase_price=item['price']
                )
                db.session.add(purchase)

        # Save all changes
        db.session.commit()

        # Clear cart
        session['cart'] = []
        session.modified = True  # Force session save
        flash(f'Purchase successful! Bought {len(valid_items)} items for ${total:.2f}. Your new balance is ${current_user.wallet_balance:.2f}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Purchase failed: {str(e)}', 'danger')

    return redirect(url_for('cart.view_cart'))



@cart_bp.route('/clear')
@login_required
def clear_cart():
    session['cart'] = []
    session.modified = True  # Force session save
    flash('Cart cleared.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/reset-session')
@login_required
def reset_session():
    """Reset all session data for debugging"""
    session.clear()
    session.modified = True
    flash('Session completely reset.', 'warning')
    return redirect(url_for('main.index'))