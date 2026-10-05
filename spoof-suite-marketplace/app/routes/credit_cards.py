from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from flask_login import current_user, login_required
import json
import requests
import os
import random
import string
import uuid
from datetime import date
from app.models import CreditCard, db
from app.utils.realistic_card_generator import generate_realistic_card

cards_bp = Blueprint('credit_cards', __name__, url_prefix='/credit-cards')

@cards_bp.route('/buy', methods=['POST'])
@login_required
def buy_card():
    wallet_balance = current_user.wallet_balance or 0.0
    if wallet_balance < 50:
        flash("Minimum wallet balance to purchase is $50. Please deposit more funds.", "danger")
        return redirect(url_for('payments.add_funds'))

    card_number = request.form.get('card_number')
    next_url = request.form.get('next') or url_for('credit_cards.debit_cards_page')
    card = CreditCard.query.filter_by(card_number=card_number).first()
    if not card:
        flash('Card not found.', 'danger')
        return redirect(next_url)

    price = card.price or 0.0
    if wallet_balance < price:
        flash('Insufficient funds.', 'danger')
        return redirect(next_url)

    current_user.wallet_balance = wallet_balance - price
    db.session.commit()

    purchased = session.get('purchased_cards', [])
    if card_number not in purchased:
        purchased.append(card_number)
        session['purchased_cards'] = purchased

    flash('Purchase successful! Card unlocked.', 'success')
    return redirect(next_url)

@cards_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    card_number = request.form.get('card_number')
    card_type = request.form.get('card_type')
    quantity = int(request.form.get('quantity', 1))
    next_url = request.form.get('next')

    if not card_number or not card_type:
        flash('Card number and type are required.', 'danger')
        return redirect(next_url or url_for('credit_cards.debit_cards_page'))

    card = CreditCard.query.filter_by(card_number=card_number, card_type=card_type).first()
    if not card:
        flash('Card not found.', 'danger')
        return redirect(next_url or url_for('credit_cards.debit_cards_page'))

    cart = session.get('cart', [])
    if not any(item.get('card_number') == card_number and item.get('card_type') == card_type for item in cart):
        cart.append({
            'card_number': card.card_number,
            'card_type': card.card_type,
            'quantity': quantity,
            'price': card.price
        })
        session['cart'] = cart
        flash('Card added to cart.', 'success')
    else:
        flash('Card already in cart.', 'info')

    return redirect(next_url or url_for('credit_cards.debit_cards_page'))

def random_name(country):
    first_names = [
        "John", "Jane", "Alice", "Bob", "Charlie", "Maria", "David", "Emily", "Michael", "Sarah",
        "Olivia", "Liam", "Noah", "Emma", "Ava", "Sophia", "James", "Benjamin", "Lucas", "Mia",
        "Ethan", "Grace", "Ella", "Jack", "Henry", "Chloe", "Amelia", "Alexander", "Daniel", "Matthew",
        "Ivan", "Olga", "Sven", "Anna", "Pierre", "Isabelle", "Carlos", "Sofia", "Ahmed", "Fatima"
    ]
    last_names = [
        "Doe", "Smith", "Brown", "Lee", "Kim", "Garcia", "Johnson", "Davis", "Miller", "Wilson",
        "Taylor", "Clark", "Walker", "Hall", "Allen", "Young", "King", "Wright", "Scott", "Green",
        "Baker", "Adams", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell",
        "Ivanov", "Petrov", "Svensson", "Dubois", "Schmidt", "Kuznetsov", "Fernandez", "Hassan", "Al-Farsi"
    ]
    usa_names = [
        "John Smith", "Jane Doe", "Alice Johnson", "Bob Brown", "Charlie Davis",
        "Maria Garcia", "David Martinez", "Emily Rodriguez", "Michael Hernandez", "Sarah Lopez"
    ]
    uk_names = [
        "Oliver Twist", "Harry Potter", "Emily Brontë", "Charlotte Brontë", "James Bond",
        "David Beckham", "Daniel Radcliffe", "Emma Watson", "Ethan Hawke", "Natalie Portman"
    ]
    canada_names = [
        "John Smith", "Emily Johnson", "Michael Brown", "Jessica Lee", "David Wilson",
        "Sarah Miller", "Chris Davis", "Ashley Clark", "Matthew Lewis", "Amanda Young"
    ]
    if country == "USA":
        return random.choice(usa_names)
    elif country == "UK":
        return random.choice(uk_names)
    elif country == "Canada":
        return random.choice(canada_names)
    else:
        return f"{random.choice(first_names)} {random.choice(last_names)}"

def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10

def generate_card_number(bin_choice):
    # bin_choice is a string like "448233"
    # Generate a random 10-digit number after the BIN
    return bin_choice + ''.join(str(random.randint(0, 9)) for _ in range(10))

def random_address(country):
    address_data = {
        "USA": {
            "streets": ["Main St", "High St", "Park Ave", "Broaddiway", "Maple Rd"],
            "cities": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "zip_format": lambda: f"{random.randint(10000, 99999)}"
        },
        "UK": {
            "streets": ["High St", "Station Rd", "Church St", "London Rd", "Victoria Ave"],
            "cities": ["London", "Manchester", "Birmingham", "Liverpool", "Leeds"],
            "zip_format": lambda: f"{random.choice(['SW1A', 'M1', 'B1', 'L1', 'LS1'])} {random.randint(1,9)}{random.choice(string.ascii_uppercase)}"
        },
        "Canada": {
            "streets": ["Queen St", "King St", "Yonge St", "Bloor St", "Bay St"],
            "cities": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
            "zip_format": lambda: f"{random.choice(string.ascii_uppercase)}{random.randint(1,9)}{random.choice(string.ascii_uppercase)} {random.randint(1,9)}{random.choice(string.ascii_uppercase)}{random.randint(1,9)}"
        },
        "China": {
            "streets": ["Nanjing Rd", "Chang'an Ave", "Wangfujing St", "Huaihai Rd", "Zhongshan Rd"],
            "cities": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu"],
            "zip_format": lambda: f"{random.randint(100000, 999999)}"
        },
        "Germany": {
            "streets": ["Hauptstrasse", "Bahnhofstrasse", "Schulstrasse", "Gartenstrasse", "Kirchstrasse"],
            "cities": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne"],
            "zip_format": lambda: f"{random.randint(10000, 99999)}"
        },
        "Spain": {
            "streets": ["Calle Mayor", "Calle de Alcalá", "Gran Vía", "Calle de Serrano", "Calle de Atocha"],
            "cities": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao"],
            "zip_format": lambda: f"{random.randint(10000, 99999)}"
        },
        "Russia": {
            "streets": ["Tverskaya St", "Arbat St", "Nevsky Prospekt", "Lenina St", "Sadovaya St"],
            "cities": ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan"],
            "zip_format": lambda: f"{random.randint(100000, 199999)}"
        },
        "France": {
            "streets": ["Rue de Rivoli", "Avenue des Champs-Élysées", "Boulevard Saint-Germain", "Rue du Bac", "Rue de la Paix"],
            "cities": ["Paris", "Lyon", "Marseille", "Toulouse", "Nice"],
            "zip_format": lambda: f"{random.randint(10000, 99999)}"
        },
        "Italy": {
            "streets": ["Via Roma", "Via Garibaldi", "Corso Vittorio Emanuele", "Via Dante", "Via Milano"],
            "cities": ["Rome", "Milan", "Naples", "Turin", "Palermo"],
            "zip_format": lambda: f"{random.randint(10000, 99999)}"
        },
        "Dubai": {
            "streets": ["Sheikh Zayed Rd", "Al Wasl Rd", "Jumeirah Beach Rd", "Al Rigga Rd", "Al Maktoum Rd"],
            "cities": ["Dubai"],
            "zip_format": lambda: f"{random.randint(10000, 99999)}"
        }
    }
    data = address_data.get(country, address_data["USA"])
    street = random.choice(data["streets"])
    city = random.choice(data["cities"])
    zip_code = data["zip_format"]()
    return f"{random.randint(100,9999)} {street}, {city}, {zip_code}, {country}"


def generate_realistic_cards(n=1000):
    bins = {
        "Visa": ["448233", "414720", "426684", "453201", "491748"],
        "MasterCard": ["545454", "528856", "520152", "524514", "557347"],
    }
    countries = ["USA", "UK", "Canada"]
    banks = {
        "USA": [
            "TD BANK, N.A.", "Bank of America", "Chase", "Wells Fargo", "Citibank", "Capital One",
            "PNC Bank", "US Bank", "Regions Bank", "Fifth Third Bank", "KeyBank", "SunTrust", "BB&T",
            "M&T Bank", "Santander Bank", "Ally Bank", "BMO Harris Bank", "Huntington Bank"
        ],
        "UK": [
            "HSBC UK", "Barclays", "Lloyds Bank", "NatWest", "Royal Bank of Scotland", "Santander UK",
            "TSB Bank", "Metro Bank", "Virgin Money", "Co-operative Bank", "Halifax"
        ],
        "Canada": [
            "RBC", "Scotiabank", "TD Canada Trust", "BMO", "CIBC", "National Bank of Canada",
            "HSBC Canada", "Laurentian Bank", "Desjardins", "ATB Financial"
        ]
    }
    states = {
        "USA": [
            "Maryland", "California", "Texas", "New York", "Florida", "Illinois", "Pennsylvania",
            "Ohio", "Georgia", "North Carolina", "Michigan", "New Jersey", "Virginia", "Washington",
            "Arizona", "Massachusetts", "Tennessee", "Indiana", "Missouri", "Wisconsin"
        ],
        "UK": [
            "England", "Scotland", "Wales", "Northern Ireland"
        ],
        "Canada": [
            "Ontario", "Quebec", "British Columbia", "Alberta", "Manitoba", "Saskatchewan",
            "Nova Scotia", "New Brunswick", "Newfoundland and Labrador", "Prince Edward Island"
        ]
    }
    cities = {
        "Maryland": ["Hyattsville", "Baltimore", "Rockville", "Silver Spring", "Bethesda", "Annapolis"],
        "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose", "Fresno", "Oakland"],
        "Texas": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth", "El Paso"],
        "New York": ["New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany"],
        "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville", "St. Petersburg", "Fort Lauderdale"],
        "Illinois": ["Chicago", "Aurora", "Naperville", "Joliet", "Springfield"],
        "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading", "Scranton"],
        "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron", "Dayton"],
        "Georgia": ["Atlanta", "Augusta", "Columbus", "Macon", "Savannah", "Athens"],
        "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem", "Fayetteville"],
        "Michigan": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor", "Lansing"],
        "New Jersey": ["Newark", "Jersey City", "Paterson", "Elizabeth", "Edison", "Trenton"],
        "Virginia": ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond", "Newport News", "Alexandria"],
        "Washington": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue", "Kent"],
        "Arizona": ["Phoenix", "Tucson", "Mesa", "Chandler", "Glendale", "Scottsdale"],
        "Massachusetts": ["Boston", "Worcester", "Springfield", "Lowell", "Cambridge", "New Bedford"],
        "Tennessee": ["Nashville", "Memphis", "Knoxville", "Chattanooga", "Clarksville", "Murfreesboro"],
        "Indiana": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend", "Carmel", "Bloomington"],
        "Missouri": ["Kansas City", "St. Louis", "Springfield", "Independence", "Columbia", "Lee's Summit"],
        "Wisconsin": ["Milwaukee", "Madison", "Green Bay", "Kenosha", "Racine", "Appleton"],
        "England": ["London", "Manchester", "Birmingham", "Liverpool", "Leeds", "Sheffield", "Bristol", "Nottingham"],
        "Scotland": ["Edinburgh", "Glasgow", "Aberdeen", "Dundee", "Inverness"],
        "Wales": ["Cardiff", "Swansea", "Newport", "Wrexham"],
        "Northern Ireland": ["Belfast", "Derry", "Lisburn", "Newry"],
        "Ontario": ["Toronto", "Ottawa", "Mississauga", "Hamilton", "London", "Kitchener"],
        "Quebec": ["Montreal", "Quebec City", "Laval", "Gatineau", "Longueuil"],
        "British Columbia": ["Vancouver", "Victoria", "Surrey", "Burnaby", "Richmond"],
        "Alberta": ["Calgary", "Edmonton", "Red Deer", "Lethbridge"],
        "Manitoba": ["Winnipeg", "Brandon", "Steinbach"],
        "Saskatchewan": ["Saskatoon", "Regina", "Prince Albert"],
        "Nova Scotia": ["Halifax", "Sydney", "Truro"],
        "New Brunswick": ["Moncton", "Saint John", "Fredericton"],
        "Newfoundland and Labrador": ["St. John's", "Corner Brook"],
        "Prince Edward Island": ["Charlottetown", "Summerside"]
    }
    addresses = [
        "7464 Village Green Terrace", "123 Main St", "456 Oak Ave", "789 Pine Rd", "22 Baker St",
        "100 King St", "55 Queen Ave", "300 Maple Rd", "17 Elm St", "88 Oakwood Blvd"
    ]
    notes = ["verified", "not checked"]

    cards = []
    seen_numbers = set()
    used_phones = set()

    while len(cards) < n:
        card_type = random.choice(list(bins.keys()))
        bin_choice = random.choice(bins[card_type])
        number = generate_card_number(bin_choice)
        if number in seen_numbers:
            continue
        seen_numbers.add(number)
        country = random.choice(countries)
        bank = random.choice(banks[country])
        state = random.choice(states[country])
        city = random.choice(cities[state])
        zip_code = str(random.randint(10000, 99999))
        address = random.choice(addresses)
        name = random_name(country)
        expiry_year = random.randint(2025, 2030)
        expiry_month = random.randint(1, 12)
        expiry = f"{expiry_month}/{str(expiry_year)[-2:]}"
        cvv = str(random.randint(100, 999))
        note = random.choice(notes)
        email = generate_email(name, state, city)
        email_pass = generate_password()
        acc_number = str(random.randint(100000000, 999999999))
        routine_number = str(random.randint(100000000000, 999999999999))
        bank_username = generate_bank_username(name, state)
        bank_password = generate_password()
        rdp_log = generate_rdp_log(name)
        ssn = generate_ssn()
        dob = generate_dob()
        phone = generate_phone(state, used_phones)
        is_verified = note == "verified" and ssn and dob and phone
        balance = round(random.uniform(100, 10000), 2) if is_verified else round(random.uniform(10, 500), 2)
        price = round(balance * (2 if is_verified else 0.5) + (50 if is_verified else 10), 2)
        card_category = random.choice(["credit", "debit"])  # <-- Add this line
        card = {
            "id": str(uuid.uuid4()),
            "credit_card_number": number,
            "credit_card_holder_name": name,
            "credit_card_expiry_date": expiry,
            "card_type": card_type,
            "credit_card_cvv": cvv,
            "issuing_bank": bank,
            "country": country,
            "state": state,
            "city": city,
            "zip": zip_code,
            "address": address,
            "balance": balance,
            "price": price,
            "card_category": card_category,
            "note": note,
            "phone": phone,
            "email": email,
            "email_pass": email_pass,
            "is_verified": is_verified,  # <-- Add this line
        }
        cards.append(card)
        new_card = CreditCard(
            card_number=number,
            card_type=card_type,
            category=card_category,
            bank=bank,
            country=country,
            state=state,
            city=city,
            zip_code=zip_code,
            address=address,
            cvv=cvv,
            expiry=expiry,
            holder_name=name,
            price=price,
            balance=balance,
            phone=phone,
            email=email,
            email_pass=email_pass,
            ssn=ssn,
            dob=dob,
            is_verified=is_verified,
            is_available=True
        )
        db.session.add(new_card)
    db.session.commit()
    random.shuffle(cards)
    return cards

# Removed old JSON-based get_credit_cards function - now using database directly

def ensure_cards_exist():
    """Ensure we have cards in the database - only generate if really needed"""
    if CreditCard.query.count() < 50:  # Only generate if we have very few cards
        print("Generating realistic cards...")
        for i in range(200):  # Generate 200 new cards
            try:
                card_data = generate_realistic_card()

                # Check if card already exists
                if CreditCard.query.filter_by(card_number=card_data["card_number"]).first():
                    continue

                card = CreditCard(
                    card_number=card_data["card_number"],
                    card_type=card_data["type"].lower(),
                    category=card_data["brand"].title(),
                    bank=card_data["bank"],
                    country=card_data["country"],
                    state=card_data["state"],
                    city=card_data["city"],
                    zip_code=card_data["zip"],
                    address=card_data["address"],
                    cvv=card_data["cvv"],
                    expiry=card_data["expiry"],
                    holder_name=card_data["cardholder_name"],
                    price=card_data["price"],
                    balance=card_data["balance"],
                    phone=card_data["phone"],
                    email=card_data["email"],
                    email_pass=card_data["email_pass"],
                    ssn=card_data["ssn"],
                    dob=card_data["dob"],
                    is_verified=card_data["is_verified"],
                    is_available=True,
                    bin_code=card_data["bin"],
                    brand=card_data["brand"],
                    level=card_data["level"],
                    prepaid=card_data["prepaid"],
                    country_flag=card_data["country_flag"],
                    note=card_data["note"],
                    validity_percent=card_data.get("validity_percent")
                )

                db.session.add(card)

                if i % 50 == 0:
                    db.session.commit()

            except Exception as e:
                print(f"Error generating card: {e}")
                continue

        db.session.commit()
        print(f"Generated cards. Total now: {CreditCard.query.count()}")

@cards_bp.route('/', methods=['GET'])
@login_required
def credit_cards_home():
    # Ensure we have cards in the database
    ensure_cards_exist()

    search = request.args.get('search', '').strip()
    query = CreditCard.query.filter_by(card_type='credit', is_available=True)

    if search and search.isdigit():
        query = query.filter(CreditCard.card_number.startswith(search))

    credit_cards = query.all()
    random.shuffle(credit_cards)

    page = int(request.args.get('page', 1))
    per_page = 10
    paginated = credit_cards[(page-1)*per_page : page*per_page]
    total_pages = (len(credit_cards) + per_page - 1) // per_page

    user_profile = {
        "full_name": current_user.username,
        "username": current_user.username,
        "email": current_user.email,
        "wallet_balance": current_user.wallet_balance or 0.0
    }

    user_cart = session.get('cart', [])
    cart_count = len(user_cart)
    cart_card_numbers = [item['card_number'] for item in user_cart if 'card_number' in item]
    purchased_cards = session.get('purchased_cards', [])

    bin_message = None
    if search and not paginated:
        bin_message = f"No cards found for BIN {search}"

    return render_template(
        'credit_cards/credit.html',
        cards=paginated,
        page=page,
        total_pages=total_pages,
        user_profile=user_profile,
        cart_count=cart_count,
        cart_card_numbers=cart_card_numbers,
        purchased_cards=purchased_cards,
        request=request,
        bin_message=bin_message
    )

@cards_bp.route('/credit', methods=['GET'])
@login_required
def credit_cards_page():
    # Ensure we have cards in the database
    ensure_cards_exist()

    search = request.args.get('search', '').strip()
    query = CreditCard.query.filter_by(card_type='credit', is_available=True)

    if search and search.isdigit():
        query = query.filter(CreditCard.card_number.startswith(search))

    credit_cards = query.all()
    random.shuffle(credit_cards)

    page = int(request.args.get('page', 1))
    per_page = 10
    paginated = credit_cards[(page-1)*per_page : page*per_page]
    total_pages = (len(credit_cards) + per_page - 1) // per_page

    user_profile = {
        "full_name": current_user.username,
        "username": current_user.username,
        "email": current_user.email,
        "wallet_balance": current_user.wallet_balance or 0.0
    }
    user_cart = session.get('cart', [])
    cart_count = len(user_cart)
    cart_card_numbers = [item['card_number'] for item in user_cart if 'card_number' in item]
    purchased_cards = session.get('purchased_cards', [])

    bin_message = None
    if search and not paginated:
        bin_message = f"No cards found for BIN {search}"

    return render_template(
        'credit_cards/credit.html',
        cards=paginated,
        page=page,
        total_pages=total_pages,
        user_profile=user_profile,
        cart_count=cart_count,
        cart_card_numbers=cart_card_numbers,
        purchased_cards=purchased_cards,
        request=request,
        bin_message=bin_message
    )

@cards_bp.route('/debit', methods=['GET'])
@login_required
def debit_cards_page():
    # Ensure we have cards in the database
    ensure_cards_exist()

    search = request.args.get('search', '').strip()
    query = CreditCard.query.filter_by(card_type='debit', is_available=True)

    if search and search.isdigit():
        query = query.filter(CreditCard.card_number.startswith(search))

    debit_cards = query.all()
    random.shuffle(debit_cards)

    page = int(request.args.get('page', 1))
    per_page = 10
    paginated = debit_cards[(page-1)*per_page : page*per_page]
    total_pages = (len(debit_cards) + per_page - 1) // per_page

    user_profile = {
        "full_name": current_user.username,
        "username": current_user.username,
        "email": current_user.email,
        "wallet_balance": current_user.wallet_balance or 0.0
    }
    user_cart = session.get('cart', [])
    cart_count = len(user_cart)
    cart_card_numbers = [item['card_number'] for item in user_cart if 'card_number' in item]
    purchased_cards = session.get('purchased_cards', [])

    bin_message = None
    if search and not paginated:
        bin_message = f"No cards found for BIN {search}"

    return render_template(
        'credit_cards/debit.html',
        cards=paginated,
        page=page,
        total_pages=total_pages,
        user_profile=user_profile,
        cart_count=cart_count,
        cart_card_numbers=cart_card_numbers,
        purchased_cards=purchased_cards,
        request=request,
        bin_message=bin_message
    )

@cards_bp.route('/delete-all-cards', methods=['POST'])
@login_required
def delete_all_cards():
    """Delete all cards from database (admin function)"""
    try:
        # Delete all cards
        deleted_count = CreditCard.query.delete()
        db.session.commit()
        flash(f'Successfully deleted {deleted_count} cards from database.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting cards: {str(e)}', 'danger')

    return redirect(url_for('credit_cards.credit_cards_home'))

@cards_bp.route('/history', methods=['GET'])
@login_required
def card_history():
    # Get purchased cards from the Purchase model - ALL cards
    from app.models import Purchase
    purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    purchased_cards = [purchase.card for purchase in purchases]
    return render_template(
        'credit_cards/credit_history.html',
        purchased_cards=purchased_cards,
        page_title="All Purchase History"
    )

@cards_bp.route('/history/credit', methods=['GET'])
@login_required
def credit_history():
    # Get purchased CREDIT cards only
    from app.models import Purchase
    purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    purchased_cards = [purchase.card for purchase in purchases if purchase.card.card_type == 'credit']
    return render_template(
        'credit_cards/credit_history.html',
        purchased_cards=purchased_cards,
        page_title="Credit Card Purchase History"
    )

@cards_bp.route('/history/debit', methods=['GET'])
@login_required
def debit_history():
    # Get purchased DEBIT cards only
    from app.models import Purchase
    purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    purchased_cards = [purchase.card for purchase in purchases if purchase.card.card_type == 'debit']
    return render_template(
        'credit_cards/credit_history.html',
        purchased_cards=purchased_cards,
        page_title="Debit Card Purchase History"
    )

def generate_email(name, state, city):
    name_part = name.lower().replace(" ", ".")
    city_part = city.lower().replace(" ", "")
    state_part = state.lower().replace(" ", "")
    domains = ["gmail.com", "yahoo.com", "outlook.com", "mail.com"]
    domain = random.choice(domains)
    num = random.randint(10, 9999)
    return f"{name_part}.{city_part}{num}@{domain}"

def generate_bank_username(name, state):
    name_part = name.lower().replace(" ", "")
    state_part = state.lower()[:3]
    num = random.randint(100, 999)
    return f"{name_part}{state_part}{num}"

def generate_rdp_log(name):
    ip = f"{random.randint(10, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
    user = name.lower().split()[0]
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"ip:{ip} user:{user} pass:{password}"

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def generate_ssn():
    # Generates a random US-style SSN (XXX-XX-XXXX)
    return f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"

def generate_dob():
    # Generates a random date of birth between 1950 and 2002
    year = random.randint(1950, 2002)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{month:02d}/{day:02d}/{year}"

credit_bins = [
    "448233", "414720", "426684", "453201", "491748", "400005", "411111", "455673", "402400", "424242",
    "403550", "404159", "405512", "406172", "407220", "408540", "409670", "410000", "412345", "413456",
    "414789", "415678", "416789", "417890", "418901", "419012", "420123", "421234", "422345", "423456",
    # ...add as many as you want...
]

debit_bins = [
    "520152", "524514", "557347", "545454", "528856", "601100", "601120", "601174", "601179", "601186",
    "601187", "601188", "601189", "601190", "601191", "601192", "601193", "601194", "601195", "601196",
    "601197", "601198", "601199", "601200", "601201", "601202", "601203", "601204", "601205", "601206",
    # ...add as many as you want...
]

def generate_phone(state=None, used_phones=None):
    # Generate a unique US-style phone number
    if used_phones is None:
        used_phones = set()
    while True:
        phone = f"{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"
        if phone not in used_phones:
            used_phones.add(phone)
            return phone