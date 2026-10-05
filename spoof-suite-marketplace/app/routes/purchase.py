from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Item, db

purchase_bp = Blueprint('purchase', __name__)

@purchase_bp.route('/shop')
@login_required
def shop():
    items = Item.query.all()
    return render_template('shop.html', items=items, wallet_balance=current_user.wallet_balance)

@purchase_bp.route('/buy/<item_id>', methods=['POST'])
@login_required
def buy_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for('purchase.shop'))
    if current_user.wallet_balance >= item.price:
        current_user.wallet_balance -= item.price
        # Add item to user's purchases, update DB, etc.
        db.session.commit()
        flash("Purchase successful!", "success")
    else:
        flash("Insufficient balance.", "danger")
    return redirect(url_for('purchase.shop'))