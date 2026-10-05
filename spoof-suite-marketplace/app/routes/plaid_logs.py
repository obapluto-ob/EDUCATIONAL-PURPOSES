from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
import random
import string
import uuid
import os
import json
from datetime import date

plaid_bp = Blueprint('plaid_logs', __name__, url_prefix='/plaid-logs')

def random_name():
    first_names = [
        "Crystal", "John", "Emily", "Michael", "Sarah", "David", "Jessica", "Matthew", "Ashley",
        "Brian", "Olivia", "Ethan", "Sophia", "Daniel", "Ava", "James", "Mia", "Benjamin", "Ella"
    ]
    last_names = [
        "Little", "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson",
        "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson"
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def random_email(name):
    domains = ["gmail.com", "yahoo.com", "outlook.com", "mail.com", "icloud.com", "protonmail.com"]
    name_part = name.lower().replace(" ", "")
    return f"{name_part}{random.randint(10,9999)}@{random.choice(domains)}"

def random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def random_ssn():
    return f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"

def random_dob():
    year = random.randint(1965, 2002)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{month:02d}/{day:02d}/{year}"

def random_phone():
    area_codes = ["410", "213", "214", "212", "305", "312", "615", "414", "718", "646", "202", "415"]
    return f"{random.choice(area_codes)}{random.randint(100,999)}{random.randint(1000,9999)}"

def random_rdp_log(name):
    ip = f"{random.randint(10,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    user = name.lower().replace(" ", "")
    password = random_password()
    return f"ip:{ip} user:{user} pass:{password}"

# Expanded BINs and banks (Visa/Mastercard, including more credit unions and major banks)
BIN_BANKS = [
    # Visa
    ("448233", "TD BANK, N.A."),
    ("414720", "Bank of America"),
    ("426684", "Chase"),
    ("453201", "Wells Fargo"),
    ("491748", "Citibank"),
    ("402400", "Navy Federal Credit Union"),
    ("400551", "PenFed Credit Union"),
    ("400005", "USAA Federal Savings Bank"),
    ("402472", "Alliant Credit Union"),
    ("400383", "SchoolsFirst Federal Credit Union"),
    ("409999", "First Tech Federal Credit Union"),
    ("401288", "BECU (Boeing Employees Credit Union)"),
    ("400003", "State Employees' Credit Union"),
    ("400006", "VyStar Credit Union"),
    ("400007", "America First Credit Union"),
    ("400008", "Golden 1 Credit Union"),
    # Mastercard
    ("545454", "Capital One"),
    ("528856", "PNC Bank"),
    ("520152", "US Bank"),
    ("524514", "Regions Bank"),
    ("557347", "Fifth Third Bank"),
    ("531144", "America First Credit Union"),
    ("542418", "Golden 1 Credit Union"),
    ("536346", "BECU (Boeing Employees Credit Union)"),
    ("536838", "State Employees' Credit Union"),
    ("536870", "VyStar Credit Union"),
    ("536871", "First Tech Federal Credit Union"),
    ("536872", "Alliant Credit Union"),
    ("536873", "SchoolsFirst Federal Credit Union"),
    ("536874", "PenFed Credit Union"),
    ("536875", "Navy Federal Credit Union"),
    ("536876", "USAA Federal Savings Bank"),
]

# Expanded routing numbers for the above banks
BANK_ROUTING_NUMBERS = {
    "TD BANK, N.A.": "031101266",
    "Bank of America": "026009593",
    "Chase": "021000021",
    "Wells Fargo": "121000248",
    "Citibank": "021000089",
    "Navy Federal Credit Union": "256074974",
    "PenFed Credit Union": "256078446",
    "USAA Federal Savings Bank": "314074269",
    "Alliant Credit Union": "271081528",
    "SchoolsFirst Federal Credit Union": "322282001",
    "Capital One": "051405515",
    "PNC Bank": "043000096",
    "US Bank": "123000220",
    "Regions Bank": "062005690",
    "Fifth Third Bank": "042000314",
    "America First Credit Union": "324377516",
    "Golden 1 Credit Union": "321175261",
    "BECU (Boeing Employees Credit Union)": "325081403",
    "State Employees' Credit Union": "253177049",
    "VyStar Credit Union": "263079276",
    "First Tech Federal Credit Union": "321180379",
}

# Realistic address book: (address, city, state, zip)
ADDRESS_BOOK = [
    ("7464 Village Green Terrace", "Hyattsville", "Maryland", "20785"),
    ("123 Main St", "San Francisco", "California", "94102"),
    ("456 Oak Ave", "Dallas", "Texas", "75201"),
    ("789 Pine Rd", "Buffalo", "New York", "14201"),
    ("22 Baker St", "Miami", "Florida", "33101"),
    ("100 King St", "Chicago", "Illinois", "60601"),
    ("55 Queen Ave", "Atlanta", "Georgia", "30301"),
    ("300 Maple Rd", "Seattle", "Washington", "98101"),
    ("17 Elm St", "Boston", "Massachusetts", "02108"),
    ("88 Oakwood Blvd", "Phoenix", "Arizona", "85001"),
    ("200 Cedar Ln", "Tacoma", "Washington", "98401"),
    ("500 Sunset Dr", "Orlando", "Florida", "32801"),
    ("900 Spruce St", "Houston", "Texas", "77001"),
    ("321 Birch Ave", "Baltimore", "Maryland", "21201"),
    ("654 Willow Rd", "Los Angeles", "California", "90001"),
    ("777 Magnolia Blvd", "Rochester", "New York", "14602"),
    ("888 Sycamore Ct", "Naperville", "Illinois", "60540"),
    ("222 Aspen Way", "Savannah", "Georgia", "31401"),
    ("333 Redwood Dr", "Mesa", "Arizona", "85201"),
    ("444 Palm St", "Springfield", "Massachusetts", "01103"),
]

def generate_plaid_logs(n):
    logs = []
    used_names = set()
    while len(logs) < n:
        name = random_name()
        if name in used_names:
            continue
        used_names.add(name)
        bin_code, bank = random.choice(BIN_BANKS)
        card_number = bin_code + ''.join(str(random.randint(0,9)) for _ in range(10))
        cvv = str(random.randint(100,999))
        expiry_month = random.randint(1,12)
        expiry_year = random.randint(25,29)
        expiry = f"{expiry_month}/{expiry_year}"
        brand = "visa" if bin_code.startswith("4") else "mastercard"
        level = random.choice(["Traditional", "Platinum", "Gold", "Classic"])
        prepaid = random.choice(["no", "yes"])
        country = "USA"
        address, city, state, zip_code = random.choice(ADDRESS_BOOK)
        phone = random_phone()
        ssn = random_ssn()
        dob = random_dob()
        email = random_email(name)
        email_pass = random_password()
        acc_number = str(random.randint(100000000,999999999))
        routine_number = BANK_ROUTING_NUMBERS.get(bank, str(random.randint(100000000,999999999)))
        bank_username = name.lower().replace(" ", "")
        bank_password = random_password()
        rdp_log = random_rdp_log(name)
        balance = round(random.uniform(100, 10000), 2)


        # Custom price logic based on balance
        if 950 <= balance <= 1050:
            price = round(random.uniform(52, 57), 2)
        elif 1950 <= balance <= 2050:
            price = round(random.uniform(90, 120), 2)
        else:
            price = max(round(balance * 0.01, 2), random.randint(50, 150))

        logs.append({
            "id": str(uuid.uuid4()),
            "card_number": card_number,
            "cvv": cvv,
            "expiry": expiry,
            "bin": bin_code,
            "type": "Debit",
            "brand": brand,
            "level": level,
            "prepaid": prepaid,
            "bank": bank,
            "country": country,
            "cardholder_name": name,
            "state": state,
            "city": city,
            "zip": zip_code,
            "address": address,
            "phone": phone,
            "ssn": ssn,
            "dob": dob,
            "email": email,
            "email_pass": email_pass,
            "acc_number": acc_number,
            "routine_number": routine_number,
            "bank_username": bank_username,
            "bank_password": bank_password,
            "rdp_log": rdp_log,
            "balance": balance,
            "price": price
        })
    return logs

def get_daily_plaid_logs():
    today = date.today().isoformat()
    cache_file = f"data/plaid_logs_{today}.json"
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)
    random.seed(today)
    n = random.randint(79, 200)
    logs = generate_plaid_logs(n)
    with open(cache_file, "w") as f:
        json.dump(logs, f)
    return logs

# Use this everywhere you need logs:
logs = get_daily_plaid_logs()

@plaid_bp.route('/', methods=['GET'])
def index():
    logs = get_daily_plaid_logs()
    page = int(request.args.get('page', 1))
    per_page = 10
    total_pages = (len(logs) + per_page - 1) // per_page
    paginated = logs[(page-1)*per_page : page*per_page]

    cart_count = len(session.get('cart', []))
    purchased_card_ids = session.get('purchased_plaid_ids', [])

    return render_template(
        'plaid_logs/plaid.html',
        cards=paginated,
        page=page,
        total_pages=total_pages,
        current_user=current_user,
        cart_count=cart_count,
        purchased_card_ids=purchased_card_ids
    )

@plaid_bp.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    card_id = request.form.get('card_id')
    action = request.form.get('action')
    next_url = request.form.get('next')

    if 'cart' not in session:
        session['cart'] = []
    logs = get_daily_plaid_logs()  # Use daily logs, not session

    cart = session['cart']

    if action == 'add':
        if not any(item.get('card_id') == card_id and item.get('card_type') == 'Plaid' for item in cart):
            card = next((c for c in logs if str(c['id']) == str(card_id)), None)
            if card:
                cart.append({
                    'card_id': card['id'],
                    'card_type': 'Plaid',
                    'quantity': 1,
                    'price': card['price']
                })
                flash('Plaid log added to cart!', 'success')
            else:
                flash('Card not found!', 'danger')
        else:
            flash('Log is already in the cart!', 'info')
    elif action == 'remove':
        cart = [item for item in cart if not (item.get('card_id') == card_id and item.get('card_type') == 'Plaid')]
        flash('Log removed from cart!', 'success')

    session['cart'] = cart
    return redirect(next_url or url_for('plaid_logs.index'))

@plaid_bp.route('/buy', methods=['POST'])
@login_required
def buy():
    wallet_balance = current_user.wallet_balance if current_user.wallet_balance is not None else 0.0
    if wallet_balance < 50:
        flash("Minimum wallet balance to purchase is $50. Please deposit more funds.", "danger")
        return redirect(url_for('payments.add_funds'))

    card_id = request.form.get('card_id')
    next_url = request.form.get('next') or url_for('plaid_logs.index')

    logs = get_daily_plaid_logs()  # Use daily logs, not session
    card = next((c for c in logs if str(c['id']) == str(card_id)), None)
    if not card:
        flash('Plaid log not found!', 'danger')
        return redirect(next_url)

    purchased = session.get('purchased_plaid_ids', [])
    if card_id not in purchased:
        purchased.append(card_id)
        session['purchased_plaid_ids'] = purchased

    flash('Plaid log purchased successfully!', 'success')
    return redirect(next_url)

@plaid_bp.route('/history', methods=['GET'])
@login_required
def history():
    logs = get_daily_plaid_logs()  # Use daily logs, not session
    purchased_ids = session.get('purchased_plaid_ids', [])
    purchased_logs = [log for log in logs if str(log['id']) in purchased_ids]

    return render_template(
        'plaid_logs/history.html',
        purchased_logs=purchased_logs,
        current_user=current_user
    )