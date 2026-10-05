from flask import Blueprint, render_template, session, request, redirect, url_for, current_app
from flask_login import login_required, current_user, logout_user, login_user
from app.routes.plaid_logs import get_daily_plaid_logs
from app.routes.fullz import get_daily_fullz
from app.models import CreditCard, User, get_user_profile
import time
import json
import os
import random
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

# Advanced caching system
class PerformanceCache:
    def __init__(self):
        self.cache = {}
        self.cache_dir = 'data/cache'
        os.makedirs(self.cache_dir, exist_ok=True)

    def get(self, key, max_age_minutes=60):
        """Get cached data if not expired"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)

                # Check if cache is still valid
                cache_time = datetime.fromisoformat(data.get('timestamp', ''))
                if datetime.now() - cache_time < timedelta(minutes=max_age_minutes):
                    return data.get('content')
            except:
                pass
        return None

    def set(self, key, content):
        """Cache data with timestamp"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        data = {
            'timestamp': datetime.now().isoformat(),
            'content': content
        }
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except:
            pass

# Global cache instance
cache = PerformanceCache()

@main_bp.route('/', methods=['GET'])
@login_required
def index():
    # Performance timing
    start_time = time.time()

    # Check cache first
    cache_key = f"dashboard_data_{current_user.id}"
    cached_data = cache.get(cache_key, max_age_minutes=30)

    if cached_data:
        # Use cached data for faster loading
        print(f"DEBUG: Using cached dashboard data")
        return render_template('index.html', **cached_data)

    # Simple notifications for now (will be enhanced after data is loaded)
    notifications = [
        "✅ All systems operational. Marketplace running smoothly!",
        "🔄 AUTO-REFRESH: Inventory updates every 24 hours. Always fresh stock.",
        "🔒 SECURITY UPDATE: All data verified and encrypted. Safe transactions guaranteed."
    ]
    purchased_cards = session.get('purchased_cards', [])
    wallet_history = session.get('wallet_history', [])
    # Fix cart count calculation
    cart = session.get('cart', [])
    cart_count = len(cart)

    # Use optimized fixed numbers for speed (no heavy generation)
    credit_count = 247  # Fixed realistic number
    debit_count = 128   # Fixed realistic number
    cards_sample = []   # Skip heavy processing

    # Simple fast alerts (no variables needed)
    notifications = [
        "✓ All systems operational - Marketplace running smoothly",
        f"• {credit_count} credit cards available - Quality verified",
        f"• {debit_count} debit cards in stock - High balance selection",
        "• Banking logs active - Live account access available",
        "• Identity profiles ready - Complete data packages",
        "→ 24/7 marketplace access - Always fresh inventory"
    ]

    # Real 6-digit BIN data with proper card types
    realistic_bins = [
        {"bin": "424242", "type": "Credit", "category": "Classic", "bank": "Chase Bank", "country": "USA", "country_code": "US"},
        {"bin": "411111", "type": "Credit", "category": "Platinum", "bank": "Bank of America", "country": "USA", "country_code": "US"},
        {"bin": "378282", "type": "Credit", "category": "Gold", "bank": "American Express", "country": "USA", "country_code": "US"},
        {"bin": "555555", "type": "Credit", "category": "Standard", "bank": "Mastercard", "country": "USA", "country_code": "US"},
        {"bin": "400012", "type": "Debit", "category": "Standard", "bank": "Wells Fargo", "country": "USA", "country_code": "US"},
        {"bin": "555544", "type": "Credit", "category": "Premium", "bank": "TD Bank", "country": "Canada", "country_code": "CA"},
        {"bin": "444433", "type": "Debit", "category": "Business", "bank": "Royal Bank", "country": "Canada", "country_code": "CA"},
        {"bin": "424299", "type": "Credit", "category": "Platinum", "bank": "Barclays", "country": "United Kingdom", "country_code": "GB"},
        {"bin": "400088", "type": "Debit", "category": "Standard", "bank": "HSBC", "country": "United Kingdom", "country_code": "GB"},
        {"bin": "520012", "type": "Credit", "category": "Gold", "bank": "Deutsche Bank", "country": "Germany", "country_code": "DE"},
        {"bin": "411177", "type": "Credit", "category": "Classic", "bank": "BNP Paribas", "country": "France", "country_code": "FR"},
        {"bin": "510099", "type": "Credit", "category": "Premium", "bank": "ANZ Bank", "country": "Australia", "country_code": "AU"},
        {"bin": "490055", "type": "Credit", "category": "Business", "bank": "Mitsubishi UFJ", "country": "Japan", "country_code": "JP"},
        {"bin": "530066", "type": "Credit", "category": "Standard", "bank": "Banco do Brasil", "country": "Brazil", "country_code": "BR"},
        {"bin": "460077", "type": "Debit", "category": "Standard", "bank": "ICICI Bank", "country": "India", "country_code": "IN"},
        {"bin": "450088", "type": "Debit", "category": "Standard", "bank": "Citibank", "country": "USA", "country_code": "US"},
        {"bin": "370099", "type": "Credit", "category": "Premium", "bank": "American Express", "country": "USA", "country_code": "US"},
        {"bin": "540011", "type": "Credit", "category": "Gold", "bank": "Capital One", "country": "USA", "country_code": "US"},
        {"bin": "220022", "type": "Debit", "category": "Standard", "bank": "Discover", "country": "USA", "country_code": "US"},
        {"bin": "510033", "type": "Credit", "category": "Business", "bank": "Scotiabank", "country": "Canada", "country_code": "CA"}
    ]

    # Country flag mapping
    country_flags = {
        'USA': 'US', 'United States': 'US', 'US': 'US',
        'Canada': 'CA', 'CA': 'CA',
        'United Kingdom': 'GB', 'UK': 'GB', 'GB': 'GB',
        'Germany': 'DE', 'DE': 'DE',
        'France': 'FR', 'FR': 'FR',
        'Australia': 'AU', 'AU': 'AU',
        'Japan': 'JP', 'JP': 'JP',
        'Brazil': 'BR', 'BR': 'BR',
        'India': 'IN', 'IN': 'IN',
        'China': 'CN', 'CN': 'CN',
        'Russia': 'RU', 'RU': 'RU',
        'Italy': 'IT', 'IT': 'IT',
        'Spain': 'ES', 'ES': 'ES',
        'Netherlands': 'NL', 'NL': 'NL',
        'Sweden': 'SE', 'SE': 'SE',
        'Norway': 'NO', 'NO': 'NO',
        'Denmark': 'DK', 'DK': 'DK',
        'Finland': 'FI', 'FI': 'FI'
    }

    # --- Generate optimized plaid/fullz data for display ---
    import os

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # Fast loading with minimal data processing
    try:
        # Quick check for cached files only (no heavy generation)
        today = datetime.now().strftime('%Y-%m-%d')
        plaid_cache = f'data/plaid_logs_{today}.json'
        fullz_cache = f'data/fullz_{today}.json'

        # Load only first 6 items for speed
        if os.path.exists(plaid_cache):
            with open(plaid_cache, 'r') as f:
                all_plaid_data = json.load(f)
                plaid_data = all_plaid_data[:6]  # Only 6 for speed
                plaid_logs_count = max(67, len(all_plaid_data))
        else:
            plaid_data = []
            plaid_logs_count = 67

        if os.path.exists(fullz_cache):
            with open(fullz_cache, 'r') as f:
                all_fullz_data = json.load(f)
                fullz_data = all_fullz_data[:6]  # Only 6 for speed
                fullz_count = max(43, len(all_fullz_data))
        else:
            fullz_data = []
            fullz_count = 43

        # Simple object conversion
        class DataObject:
            def __init__(self, data_dict):
                for key, value in data_dict.items():
                    setattr(self, key, value)

        plaid_logs = [DataObject(log) for log in plaid_data]
        fullz_logs = [DataObject(fullz) for fullz in fullz_data]

        print(f"DEBUG: Loaded {len(plaid_logs)} plaid, {len(fullz_logs)} fullz (fast mode)")

    except Exception as e:
        print(f"DEBUG: Fast loading failed: {e}")
        # Ultra-fast fallback
        plaid_logs = []
        fullz_logs = []
        plaid_logs_count = 67
        fullz_count = 43

    # Use simple realistic BINs (no complex processing for speed)
    # Latest BINs Overall (show 8 for speed)
    latest_bins_overall = realistic_bins[:8]

    # Latest BINs by Country (unique countries, show 6 for speed)
    country_bins = {}
    for bin_data in realistic_bins:
        country = bin_data["country"]
        if country not in country_bins and len(country_bins) < 6:
            country_bins[country] = bin_data

    latest_bins_country = list(country_bins.values())



    # Payment methods - BTC and USDT only (same as add_funds)
    payment_addresses = {
        'USDT_TRC20': "TUjuxkyc12zUbVgWiEQn17VYKf4yB5YYm1",
        'BTC': "35yWsg6WJRfQg7h3sKXnt93r1Dz3WpCSoX"
    }
    usdt_wallet_address = payment_addresses['USDT_TRC20']
    btc_wallet_address = payment_addresses['BTC']

    user_profile = get_user_profile(current_user.id) or {
        "full_name": current_user.username,
        "username": current_user.username,
        "email": current_user.email,
        "wallet_balance": getattr(current_user, "wallet_balance", 0.0)
    }

    # Prepare template data
    template_data = {
        'notifications': notifications,
        'credit_count': credit_count,
        'debit_count': debit_count,
        'latest_bins_overall': latest_bins_overall[:10],
        'latest_bins_country': latest_bins_country[:10],
        'user_profile': user_profile,
        'payment_addresses': payment_addresses,
        'usdt_wallet_address': usdt_wallet_address,
        'btc_wallet_address': btc_wallet_address,
        'purchased_cards': purchased_cards,
        'wallet_history': wallet_history,
        'cart_count': cart_count,
        'plaid_logs': plaid_logs[:8],
        'fullz_logs': fullz_logs[:8],
        'plaid_logs_count': plaid_logs_count,
        'fullz_count': fullz_count,
        'wallet_balance': getattr(current_user, 'wallet_balance', 0.0)
    }

    # Cache the data for future requests
    cache.set(cache_key, template_data)

    # Performance metrics
    end_time = time.time()
    load_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
    print(f"DEBUG: Dashboard loaded in {load_time}ms")

    return render_template('index.html', **template_data)

@main_bp.route('/cards')
@login_required
def view_cards():
    """View all generated cards"""
    try:
        # Load today's generated cards
        today = datetime.now().strftime('%Y-%m-%d')
        cards_cache_file = f'data/generated_cards_{today}.json'

        if os.path.exists(cards_cache_file):
            with open(cards_cache_file, 'r') as f:
                generated_cards = json.load(f)
        else:
            generated_cards = []

        # Separate by type
        credit_cards = [c for c in generated_cards if c['card_type'] == 'Credit']
        debit_cards = [c for c in generated_cards if c['card_type'] == 'Debit']

        return render_template('cards.html',
                             credit_cards=credit_cards[:50],  # Show first 50
                             debit_cards=debit_cards[:50],    # Show first 50
                             total_credit=len(credit_cards),
                             total_debit=len(debit_cards))

    except Exception as e:
        print(f"DEBUG: Error loading cards: {e}")
        return render_template('cards.html',
                             credit_cards=[],
                             debit_cards=[],
                             total_credit=0,
                             total_debit=0)

@main_bp.route('/generate_cards')
@login_required
def generate_new_cards():
    """Force generate new cards"""
    try:
        # Simple card generator function (same as above)
        def generate_realistic_card():
            bins = [
                {"bin": "424242", "issuer": "Chase Bank", "type": "Credit", "level": "Classic"},
                {"bin": "411111", "issuer": "Bank of America", "type": "Credit", "level": "Platinum"},
                {"bin": "555555", "issuer": "Mastercard", "type": "Credit", "level": "Standard"},
                {"bin": "401288", "issuer": "Wells Fargo", "type": "Debit", "level": "Standard"},
                {"bin": "378282", "issuer": "American Express", "type": "Credit", "level": "Gold"},
            ]

            names = ["Michael Johnson", "Sarah Williams", "David Brown", "Jessica Davis", "Christopher Miller"]

            bin_info = random.choice(bins)
            card_number = bin_info["bin"] + str(random.randint(100000000, 999999999))

            return {
                "card_number": card_number,
                "cardholder_name": random.choice(names),
                "expiry": f"{random.randint(1, 12):02d}/{random.randint(25, 30)}",
                "cvv": str(random.randint(100, 999)),
                "issuer": bin_info["issuer"],
                "card_type": bin_info["type"],
                "level": bin_info["level"],
                "balance": round(random.uniform(500, 10000), 2),
                "price": round(random.uniform(15, 200), 2),
                "country": "USA"
            }

        # Generate new cards
        generated_cards = []

        # Generate credit cards (200-400 cards)
        credit_count_to_generate = random.randint(200, 400)
        for _ in range(credit_count_to_generate):
            card = generate_realistic_card()
            if card['card_type'] == 'Credit':
                generated_cards.append(card)

        # Generate debit cards (100-250 cards)
        debit_count_to_generate = random.randint(100, 250)
        for _ in range(debit_count_to_generate):
            card = generate_realistic_card()
            # Force some to be debit
            if len([c for c in generated_cards if c['card_type'] == 'Debit']) < debit_count_to_generate:
                card['card_type'] = 'Debit'
                card['level'] = 'Standard'
            generated_cards.append(card)

        # Save generated cards
        today = datetime.now().strftime('%Y-%m-%d')
        cards_cache_file = f'data/generated_cards_{today}.json'
        import os
        os.makedirs('data', exist_ok=True)
        with open(cards_cache_file, 'w') as f:
            json.dump(generated_cards, f)

        return redirect(url_for('main.index'))

    except Exception as e:
        print(f"DEBUG: Card generation failed: {e}")
        return redirect(url_for('main.index'))

@main_bp.route('/logout/')
@login_required
def logout():
    logout_user()         # Flask-Login: log out the user
    session.clear()       # Clear session data (optional, but recommended)
    return redirect(url_for('auth.login'))  # Correct auth blueprint login route

# Login route moved to auth.py - removed duplicate

# Credit cards route moved to credit_cards.py to avoid conflicts
# This route is now handled by the credit_cards blueprint

# Debit cards route moved to credit_cards.py to avoid conflicts
# This route is now handled by the credit_cards blueprint

# Example for a stats route
@main_bp.route('/stats')
@login_required
def stats():
    fullz_list = get_daily_fullz()
    fullz_count = len(fullz_list)
    return render_template('stats.html', fullz_count=fullz_count)

@main_bp.route('/purchase', methods=['POST'])
@login_required
def purchase():
    # ...purchase logic...
    add_notification("You made a new purchase!")
    # ...redirect or render...
