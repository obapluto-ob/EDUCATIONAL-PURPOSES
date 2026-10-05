"""
Realistic Card Generator with authentic BINs, locations, and card details
"""
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Real BIN data with authentic bank information
REAL_BINS = {
    # VISA Credit Cards
    "448233": {"bank": "TD BANK, N.A.", "type": "credit", "brand": "visa", "level": "Traditional", "country": "USA"},
    "414720": {"bank": "Bank of America", "type": "credit", "brand": "visa", "level": "Platinum", "country": "USA"},
    "426684": {"bank": "Chase", "type": "credit", "brand": "visa", "level": "Gold", "country": "USA"},
    "453201": {"bank": "Wells Fargo", "type": "credit", "brand": "visa", "level": "Classic", "country": "USA"},
    "491748": {"bank": "Citibank", "type": "credit", "brand": "visa", "level": "Signature", "country": "USA"},
    "400005": {"bank": "Capital One", "type": "credit", "brand": "visa", "level": "Platinum", "country": "USA"},
    "411111": {"bank": "PNC Bank", "type": "credit", "brand": "visa", "level": "Traditional", "country": "USA"},
    "455673": {"bank": "US Bank", "type": "credit", "brand": "visa", "level": "Gold", "country": "USA"},
    
    # VISA Debit Cards
    "448234": {"bank": "TD BANK, N.A.", "type": "debit", "brand": "visa", "level": "Traditional", "country": "USA"},
    "414721": {"bank": "Bank of America", "type": "debit", "brand": "visa", "level": "Classic", "country": "USA"},
    "426685": {"bank": "Chase", "type": "debit", "brand": "visa", "level": "Traditional", "country": "USA"},
    "453202": {"bank": "Wells Fargo", "type": "debit", "brand": "visa", "level": "Classic", "country": "USA"},
    
    # MasterCard Credit Cards
    "520152": {"bank": "Regions Bank", "type": "credit", "brand": "mastercard", "level": "World", "country": "USA"},
    "524514": {"bank": "Fifth Third Bank", "type": "credit", "brand": "mastercard", "level": "Platinum", "country": "USA"},
    "557347": {"bank": "KeyBank", "type": "credit", "brand": "mastercard", "level": "Gold", "country": "USA"},
    "545454": {"bank": "SunTrust", "type": "credit", "brand": "mastercard", "level": "World Elite", "country": "USA"},
    "528856": {"bank": "BB&T", "type": "credit", "brand": "mastercard", "level": "Platinum", "country": "USA"},
    
    # MasterCard Debit Cards
    "520153": {"bank": "Regions Bank", "type": "debit", "brand": "mastercard", "level": "Standard", "country": "USA"},
    "524515": {"bank": "Fifth Third Bank", "type": "debit", "brand": "mastercard", "level": "Traditional", "country": "USA"},
    "557348": {"bank": "KeyBank", "type": "debit", "brand": "mastercard", "level": "Standard", "country": "USA"},
    
    # International Cards
    "424242": {"bank": "HSBC UK", "type": "credit", "brand": "visa", "level": "Platinum", "country": "UK"},
    "455555": {"bank": "Barclays", "type": "credit", "brand": "visa", "level": "Gold", "country": "UK"},
    "533333": {"bank": "Lloyds Bank", "type": "credit", "brand": "mastercard", "level": "World", "country": "UK"},
    "444444": {"bank": "RBC", "type": "credit", "brand": "visa", "level": "Platinum", "country": "Canada"},
    "555555": {"bank": "Scotiabank", "type": "credit", "brand": "mastercard", "level": "World Elite", "country": "Canada"},
}

# Country flags and details
COUNTRY_DATA = {
    "USA": {"flag": "🇺🇸", "currency": "USD", "phone_format": "+1-{area}-{exchange}-{number}"},
    "UK": {"flag": "🇬🇧", "currency": "GBP", "phone_format": "+44-{area}-{number}"},
    "Canada": {"flag": "🇨🇦", "currency": "CAD", "phone_format": "+1-{area}-{exchange}-{number}"},
    "Germany": {"flag": "🇩🇪", "currency": "EUR", "phone_format": "+49-{area}-{number}"},
    "France": {"flag": "🇫🇷", "currency": "EUR", "phone_format": "+33-{area}-{number}"},
    "Australia": {"flag": "🇦🇺", "currency": "AUD", "phone_format": "+61-{area}-{number}"},
}

# Realistic address data by state/region
ADDRESS_DATA = {
    "Maryland": {
        "cities": ["Hyattsville", "Baltimore", "Rockville", "Silver Spring", "Bethesda", "Annapolis"],
        "streets": ["Village Green Terrace", "Main Street", "Oak Avenue", "Pine Road", "Elm Street", "Maple Drive"],
        "zip_codes": ["20785", "21201", "20852", "20910", "20814", "21401"]
    },
    "California": {
        "cities": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose", "Fresno"],
        "streets": ["Sunset Boulevard", "Hollywood Drive", "Ocean Avenue", "Market Street", "Broadway", "First Street"],
        "zip_codes": ["90210", "94102", "92101", "95814", "95110", "93650"]
    },
    "Texas": {
        "cities": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth", "El Paso"],
        "streets": ["Main Street", "Congress Avenue", "Lamar Boulevard", "Westheimer Road", "Richmond Avenue"],
        "zip_codes": ["77001", "75201", "78701", "78201", "76101", "79901"]
    },
    "New York": {
        "cities": ["New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany"],
        "streets": ["Broadway", "Fifth Avenue", "Wall Street", "Madison Avenue", "Park Avenue", "Lexington Avenue"],
        "zip_codes": ["10001", "14201", "14601", "10701", "13201", "12201"]
    },
    "Florida": {
        "cities": ["Miami", "Orlando", "Tampa", "Jacksonville", "St. Petersburg", "Fort Lauderdale"],
        "streets": ["Ocean Drive", "Collins Avenue", "Biscayne Boulevard", "International Drive", "Beach Boulevard"],
        "zip_codes": ["33101", "32801", "33601", "32201", "33701", "33301"]
    }
}

# Realistic names by ethnicity/region
NAMES_DATA = {
    "american": {
        "first": ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
                 "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen",
                 "Crystal", "Ashley", "Amanda", "Nicole", "Stephanie", "Melissa", "Rebecca", "Laura", "Kimberly"],
        "last": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
                "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Little"]
    }
}

def luhn_checksum(card_number: str) -> bool:
    """Validate card number using Luhn algorithm"""
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10 == 0

def generate_valid_card_number(bin_code: str) -> str:
    """Generate a valid card number with Luhn checksum"""
    # Generate 9 random digits (16 total - 6 BIN - 1 check digit)
    partial_number = bin_code + ''.join([str(random.randint(0, 9)) for _ in range(9)])
    
    # Calculate check digit
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(partial_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    
    check_digit = (10 - (checksum % 10)) % 10
    return partial_number + str(check_digit)

def generate_realistic_name() -> str:
    """Generate a realistic American name"""
    first_name = random.choice(NAMES_DATA["american"]["first"])
    last_name = random.choice(NAMES_DATA["american"]["last"])
    return f"{first_name} {last_name}"

def generate_address(state: str) -> Tuple[str, str, str, str]:
    """Generate realistic address for given state with proper city/zip matching"""
    if state not in ADDRESS_DATA:
        state = "Maryland"  # Default fallback

    data = ADDRESS_DATA[state]
    street_number = random.randint(100, 9999)
    street_name = random.choice(data["streets"])

    # Enhanced city/zip matching
    cities = data["cities"]
    zip_codes = data["zip_codes"]

    # If we have the same number of cities and zip codes, match them
    if len(cities) == len(zip_codes):
        city_index = random.randint(0, len(cities) - 1)
        city = cities[city_index]
        zip_code = zip_codes[city_index]
    else:
        # Fallback to random selection
        city = random.choice(cities)
        zip_code = random.choice(zip_codes)

    address = f"{street_number} {street_name}"
    return address, city, state, zip_code

def generate_phone_number(country: str = "USA") -> str:
    """Generate realistic phone number with proper country codes"""
    country_phone_formats = {
        "USA": {
            "code": "+1",
            "format": lambda: f"+1 ({random.choice(['212', '646', '917', '718', '347', '213', '323', '424', '310', '818', '312', '773', '872', '202', '305', '786', '954', '713', '281', '832', '215', '267', '445', '404', '678', '470', '617', '857', '781'])}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        },
        "Canada": {
            "code": "+1",
            "format": lambda: f"+1 ({random.choice(['416', '647', '437', '905', '289', '365', '514', '438', '613', '343'])}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        },
        "UK": {
            "code": "+44",
            "format": lambda: f"+44 {random.choice(['20', '121', '131', '141', '151', '161', '191'])} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        },
        "Germany": {
            "code": "+49",
            "format": lambda: f"+49 {random.choice(['30', '40', '69', '89', '221', '211', '228'])} {random.randint(10000000, 99999999)}"
        },
        "France": {
            "code": "+33",
            "format": lambda: f"+33 {random.choice(['1', '2', '3', '4', '5'])} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
        },
        "Australia": {
            "code": "+61",
            "format": lambda: f"+61 {random.choice(['2', '3', '7', '8'])} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        },
        "Japan": {
            "code": "+81",
            "format": lambda: f"+81 {random.choice(['3', '6', '45', '52', '75', '92'])} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        },
        "Brazil": {
            "code": "+55",
            "format": lambda: f"+55 {random.choice(['11', '21', '31', '41', '51', '61', '71', '81', '85'])} {random.randint(10000, 99999)}-{random.randint(1000, 9999)}"
        },
        "Italy": {
            "code": "+39",
            "format": lambda: f"+39 {random.choice(['02', '06', '011', '051', '055', '081', '091'])} {random.randint(1000000, 9999999)}"
        },
        "Spain": {
            "code": "+34",
            "format": lambda: f"+34 {random.choice(['91', '93', '95', '96', '98'])} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
        }
    }

    if country in country_phone_formats:
        return country_phone_formats[country]["format"]()
    else:
        # Default format for unknown countries
        return f"+{random.randint(1, 999)} {random.randint(1000000000, 9999999999)}"

def generate_national_id(country: str = "USA") -> str:
    """Generate realistic national ID based on country (not all countries use SSN)"""
    country_id_formats = {
        "USA": {
            "name": "SSN",
            "format": lambda: f"{random.choice(list(range(1, 666)) + list(range(667, 900))):03d}-{random.randint(1, 99):02d}-{random.randint(1, 9999):04d}"
        },
        "Canada": {
            "name": "SIN",
            "format": lambda: f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
        },
        "UK": {
            "name": "NINO",
            "format": lambda: f"{random.choice(['AB', 'CE', 'CH', 'CR', 'EA', 'EB', 'EG', 'EH', 'EL', 'EM', 'EP', 'ER', 'ES', 'ET', 'EW', 'EX', 'EY', 'EZ'])}{random.randint(10, 99)}{random.randint(10, 99)}{random.randint(10, 99)}{random.choice(['A', 'B', 'C', 'D'])}"
        },
        "Germany": {
            "name": "Steuer-ID",
            "format": lambda: f"{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
        },
        "France": {
            "name": "INSEE",
            "format": lambda: f"{random.choice([1, 2])}{random.randint(10, 99)}{random.randint(1, 12):02d}{random.randint(1, 99):02d}{random.randint(100, 999)}{random.randint(10, 99)}"
        },
        "Australia": {
            "name": "TFN",
            "format": lambda: f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
        },
        "Japan": {
            "name": "My Number",
            "format": lambda: f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        },
        "Brazil": {
            "name": "CPF",
            "format": lambda: f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
        },
        "Italy": {
            "name": "Codice Fiscale",
            "format": lambda: f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=6))}{random.randint(10, 99)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=1))}{random.randint(10, 99)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=1))}{random.randint(100, 999)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=1))}"
        },
        "Spain": {
            "name": "DNI",
            "format": lambda: f"{random.randint(10000000, 99999999)}-{random.choice('TRWAGMYFPDXBNJZSQVHLCKE')}"
        }
    }

    if country in country_id_formats:
        return country_id_formats[country]["format"]()
    else:
        # Default format for unknown countries
        return f"{random.randint(100000000, 999999999)}"

def get_id_type_name(country: str = "USA") -> str:
    """Get the national ID type name for a country"""
    id_names = {
        "USA": "SSN",
        "Canada": "SIN",
        "UK": "NINO",
        "Germany": "Steuer-ID",
        "France": "INSEE",
        "Australia": "TFN",
        "Japan": "My Number",
        "Brazil": "CPF",
        "Italy": "Codice Fiscale",
        "Spain": "DNI"
    }
    return id_names.get(country, "National ID")

def generate_dob() -> str:
    """Generate realistic date of birth (always generate for potential verified cards)"""
    # Generate DOB for adults (18-65 years old)
    current_year = datetime.now().year
    birth_year = random.randint(current_year - 65, current_year - 18)
    birth_month = random.randint(1, 12)

    # Handle different month lengths
    if birth_month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif birth_month in [4, 6, 9, 11]:
        max_day = 30
    else:  # February
        max_day = 28  # Keep it simple, avoid leap year complexity

    birth_day = random.randint(1, max_day)
    return f"{birth_month:02d}/{birth_day:02d}/{birth_year}"

def generate_email(name: str) -> str:
    """Generate realistic email"""
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "icloud.com"]
    name_part = name.lower().replace(" ", ".")
    numbers = random.randint(10, 9999) if random.random() < 0.6 else ""
    return f"{name_part}{numbers}@{random.choice(domains)}"

def generate_password() -> str:
    """Generate realistic password"""
    patterns = [
        lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=8)),
        lambda: f"{random.choice(['Password', 'Secret', 'Key'])}{random.randint(1, 999)}",
        lambda: f"{random.choice(NAMES_DATA['american']['first'])}{random.randint(10, 99)}",
    ]
    return random.choice(patterns)()

def generate_realistic_card() -> Dict:
    """Generate a single realistic card with all details"""
    # Import here to avoid circular imports
    try:
        from .bin_manager import get_all_bins
        all_bins = get_all_bins()
    except:
        all_bins = REAL_BINS

    # Select random BIN
    bin_code = random.choice(list(all_bins.keys()))
    bin_info = all_bins[bin_code]
    
    # Generate card number with valid Luhn checksum
    card_number = generate_valid_card_number(bin_code)
    
    # Generate card details
    name = generate_realistic_name()
    country = bin_info["country"]
    
    # Generate location based on country
    if country == "USA":
        state = random.choice(list(ADDRESS_DATA.keys()))
        address, city, state, zip_code = generate_address(state)
    else:
        # For international cards, use simplified data
        state = country
        city = f"{country} City"
        zip_code = f"{random.randint(10000, 99999)}"
        address = f"{random.randint(100, 999)} Main Street"
    
    # Generate other details
    cvv = str(random.randint(100, 999))
    exp_month = random.randint(1, 12)
    exp_year = random.randint(25, 30)
    expiry = f"{exp_month}/{exp_year}"
    
    phone = generate_phone_number(country)
    ssn = generate_national_id(country)  # Country-specific ID (SSN/SIN/NINO/etc)
    dob = generate_dob()
    email = generate_email(name)
    email_pass = generate_password()
    
    # Generate financial details with new logic
    # Always generate real data, but control display based on verification
    is_verified = random.random() < 0.35  # 35% chance of verified

    if is_verified:
        # Verified cards: Show balance ($99-$9999), price = 2% of balance
        # Start at 55% validity, then 60%, then 80%
        balance = round(random.uniform(99, 9999), 2)
        price = round(balance * 0.02, 2)  # Exactly 2% of balance
        note = "verified"
        validity_percent = random.choice([55, 60, 80])  # Verified cards start at 55%
    else:
        # Not verified cards: No balance shown, price based on validity percentage
        balance = None  # No balance for unverified cards
        validity_percent = random.choice([80, 60, 55, 45, 35])  # Valid percentages including low ones

        # Price calculation based on validity percentage
        if validity_percent == 80:
            price = round(random.uniform(45, 85), 2)
        elif validity_percent == 60:
            price = round(random.uniform(25, 55), 2)
        elif validity_percent == 55:
            price = round(random.uniform(15, 35), 2)
        elif validity_percent == 45:
            price = round(random.uniform(8, 18), 2)
        else:  # 35%
            price = round(random.uniform(3, 12), 2)

        note = "not checked"
    
    # Determine if prepaid
    prepaid = "yes" if random.random() < 0.3 else "no"
    
    return {
        "id": str(uuid.uuid4()),
        "card_number": card_number,
        "cvv": cvv,
        "expiry": expiry,
        "bin": bin_code,
        "type": bin_info["type"].title(),
        "brand": bin_info["brand"],
        "level": bin_info["level"],
        "prepaid": prepaid,
        "bank": bin_info["bank"],
        "country": country,
        "country_flag": COUNTRY_DATA.get(country, {}).get("flag", "🏳️"),
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
        "note": note,
        "is_verified": is_verified,
        "balance": balance,
        "validity_percent": validity_percent,
        "price": price,
        "created_at": datetime.utcnow().isoformat()
    }

def generate_multiple_cards(count: int = 100) -> List[Dict]:
    """Generate multiple realistic cards"""
    cards = []
    used_numbers = set()
    
    while len(cards) < count:
        card = generate_realistic_card()
        if card["card_number"] not in used_numbers:
            used_numbers.add(card["card_number"])
            cards.append(card)
    
    return cards
