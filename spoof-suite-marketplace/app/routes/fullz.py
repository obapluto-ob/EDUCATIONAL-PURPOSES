from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from faker import Faker
import random
import os
import json
from datetime import date

fullz_bp = Blueprint('fullz', __name__)
fake = Faker('en_US')

def generate_fullz(n=10):
    fullz_list = []
    fake.unique.clear()
    used_ssn = set()
    used_email = set()
    used_phone = set()
    used_dl = set()
    used_bank_acc = set()

    banks = [
        {"name": "Bank of America", "routing": "026009593"},
        {"name": "JPMorgan Chase", "routing": "021000021"},
        {"name": "Wells Fargo", "routing": "121000248"},
        {"name": "Citibank", "routing": "021000089"},
        {"name": "US Bank", "routing": "091000022"},
        {"name": "PNC Bank", "routing": "043000096"},
        {"name": "Capital One", "routing": "051409515"},
        {"name": "TD Bank", "routing": "031101266"},
        {"name": "HSBC Bank USA", "routing": "022000020"},
        {"name": "Regions Bank", "routing": "062005690"}
    ]

    for _ in range(n):
        bank = random.choice(banks)
        bank_name = bank["name"]
        routing = bank["routing"]

        first = fake.first_name()
        last = fake.last_name()
        name = f"{first} {last}"
        email_domain = random.choice(["gmail.com", "yahoo.com", "outlook.com"])
        email = f"{first.lower()}.{last.lower()}{random.randint(100,999)}@{email_domain}"
        while email in used_email:
            email = f"{first.lower()}.{last.lower()}{random.randint(100,999)}@{email_domain}"
        used_email.add(email)

        address = fake.street_address()
        city = fake.city()
        state = fake.state_abbr()
        zip_code = fake.zipcode_in_state(state)
        full_address = f"{address}, {city}, {state} {zip_code}"

        ssn = fake.unique.ssn()
        phone = fake.numerify(text="+1-###-###-####")
        while phone in used_phone:
            phone = fake.numerify(text="+1-###-###-####")
        used_phone.add(phone)

        dl = f"{state}{random.randint(1000000,9999999)}"
        while dl in used_dl:
            dl = f"{state}{random.randint(1000000,9999999)}"
        used_dl.add(dl)

        dob = fake.date_of_birth(minimum_age=21, maximum_age=70).strftime('%m/%d/%Y')

        bank_acc = str(random.randint(1000000000,9999999999))
        while bank_acc in used_bank_acc:
            bank_acc = str(random.randint(1000000000,9999999999))
        used_bank_acc.add(bank_acc)

        bank_user = f"{first.lower()}{last.lower()}{random.randint(10,99)}"
        bank_pass = fake.password(length=10)

        credit_report = f"Score: {random.randint(600, 800)}, Open Accounts: {random.randint(1, 5)}, Delinquencies: {random.randint(0, 2)}"
        twofa_sms = phone
        security_questions = [
            f"Mother's maiden name: {fake.last_name()}",
            f"First pet's name: {fake.first_name()}",
            f"Favorite teacher: {fake.name()}"
        ]
        balance = round(random.uniform(1000, 10000), 2)
        price = round(random.uniform(50, 200), 2)
        log_id = fake.uuid4()

        fullz_list.append({
            "log_id": log_id,
            "name": name,
            "dob": dob,
            "ssn": ssn,
            "address": full_address,
            "zip": zip_code,
            "state": state,
            "city": city,
            "phone": phone,
            "email": email,
            "dl": dl,
            "bank_acc": bank_acc,
            "routing": routing,
            "bank_name": bank_name,
            "bank_user": bank_user,
            "bank_pass": bank_pass,
            "credit_report": credit_report,
            "twofa_sms": twofa_sms,
            "security_questions": security_questions,
            "balance": balance,
            "price": price
        })
    return fullz_list

def get_daily_fullz():
    today = date.today().isoformat()
    cache_file = f"data/fullz_{today}.json"
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)
    random.seed(today)
    n = random.randint(70, 200)
    fullz_list = generate_fullz(n)
    with open(cache_file, "w") as f:
        json.dump(fullz_list, f)
    return fullz_list

@fullz_bp.route('/fullz-usa/')
@login_required
def fullz_usa():
    page = int(request.args.get('page', 1))
    per_page = 5
    fullz_list = get_daily_fullz()
    start = (page - 1) * per_page
    end = start + per_page
    page_logs = fullz_list[start:end]
    total_pages = (len(fullz_list) + per_page - 1) // per_page
    return render_template(
        'fullz/fullz_usa.html',
        fullz_list=page_logs,
        page=page,
        total_pages=total_pages,
        username=current_user.username,
        user_balance=getattr(current_user, 'balance', 0)
    )

@fullz_bp.route('/fullz-usa/next')
@login_required
def fullz_usa_next():
    fullz_list = get_daily_fullz()
    return render_template('fullz/fullz_usa.html', fullz_list=fullz_list)

@fullz_bp.route('/buy-fullz', methods=['POST'])
@login_required
def buy_fullz():
    log_id = request.form.get('log_id')
    fullz_list = get_daily_fullz()
    purchased_fullz = [log for log in fullz_list if str(log['log_id']) == str(log_id)]
    return render_template('fullz/history.html', purchased_fullz=purchased_fullz)

@fullz_bp.route('/fullz-history/')
@login_required
def history():
    purchased_fullz = []  # Replace with actual logic if you store purchases
    return render_template('fullz/history.html', purchased_fullz=purchased_fullz)