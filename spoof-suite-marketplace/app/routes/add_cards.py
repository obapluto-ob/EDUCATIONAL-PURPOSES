import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import CreditCard, User

app = create_app()
with app.app_context():
    user = User.query.first()
    card1 = CreditCard(
        user_id=user.id,
        card_number="4111111111111111",
        card_type="credit",
        category="platinum",
        bank="Bank of America",
        country="USA"
    )
    db.session.add(card1)

    card2 = CreditCard(
        user_id=user.id,
        card_number="5500000000000004",
        card_type="debit",
        category="standard",
        bank="Chase",
        country="USA"
    )
    db.session.add(card2)

    db.session.commit()
    print("Cards added!")