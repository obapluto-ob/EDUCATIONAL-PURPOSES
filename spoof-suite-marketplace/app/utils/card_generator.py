"""
Enhanced Card Generation System
Advanced algorithms for realistic card data generation
"""
import random
import string
from datetime import datetime, timedelta
import re

class AdvancedCardGenerator:
    """Advanced card generation with realistic algorithms"""
    
    def __init__(self):
        # Enhanced BIN database with real issuer information
        self.enhanced_bins = {
            # Visa BINs
            "424242": {"issuer": "Chase Bank", "country": "USA", "type": "Credit", "level": "Classic"},
            "411111": {"issuer": "Bank of America", "country": "USA", "type": "Credit", "level": "Platinum"},
            "401288": {"issuer": "Wells Fargo", "country": "USA", "type": "Debit", "level": "Standard"},
            "450875": {"issuer": "Citibank", "country": "USA", "type": "Credit", "level": "Gold"},
            "478542": {"issuer": "Capital One", "country": "USA", "type": "Credit", "level": "Premium"},
            
            # Mastercard BINs
            "555555": {"issuer": "Mastercard", "country": "USA", "type": "Credit", "level": "Standard"},
            "530131": {"issuer": "TD Bank", "country": "Canada", "type": "Credit", "level": "Premium"},
            "520012": {"issuer": "Deutsche Bank", "country": "Germany", "type": "Credit", "level": "Gold"},
            "510099": {"issuer": "ANZ Bank", "country": "Australia", "type": "Credit", "level": "Premium"},
            
            # American Express BINs
            "378282": {"issuer": "American Express", "country": "USA", "type": "Credit", "level": "Gold"},
            "371449": {"issuer": "American Express", "country": "USA", "type": "Credit", "level": "Platinum"},
            "370099": {"issuer": "American Express", "country": "USA", "type": "Credit", "level": "Premium"},
            
            # Discover BINs
            "601111": {"issuer": "Discover", "country": "USA", "type": "Credit", "level": "Standard"},
            "622126": {"issuer": "Discover", "country": "USA", "type": "Debit", "level": "Standard"},
        }
        
        # Realistic cardholder names database
        self.realistic_names = [
            "Michael Johnson", "Sarah Williams", "David Brown", "Jessica Davis",
            "Christopher Miller", "Ashley Wilson", "Matthew Moore", "Amanda Taylor",
            "Joshua Anderson", "Jennifer Thomas", "Andrew Jackson", "Elizabeth White",
            "Daniel Harris", "Stephanie Martin", "James Thompson", "Michelle Garcia",
            "Robert Martinez", "Lisa Robinson", "John Clark", "Nancy Rodriguez",
            "William Lewis", "Karen Lee", "Richard Walker", "Betty Hall",
            "Charles Allen", "Helen Young", "Thomas Hernandez", "Sandra King"
        ]
        
        # Enhanced address database with real ZIP codes
        self.realistic_addresses = [
            {"address": "123 Main Street", "city": "New York", "state": "NY", "zip": "10001"},
            {"address": "456 Oak Avenue", "city": "Los Angeles", "state": "CA", "zip": "90210"},
            {"address": "789 Pine Road", "city": "Chicago", "state": "IL", "zip": "60601"},
            {"address": "321 Elm Street", "city": "Houston", "state": "TX", "zip": "77001"},
            {"address": "654 Maple Drive", "city": "Phoenix", "state": "AZ", "zip": "85001"},
            {"address": "987 Cedar Lane", "city": "Philadelphia", "state": "PA", "zip": "19101"},
            {"address": "147 Birch Way", "city": "San Antonio", "state": "TX", "zip": "78201"},
            {"address": "258 Spruce Court", "city": "San Diego", "state": "CA", "zip": "92101"},
            {"address": "369 Willow Place", "city": "Dallas", "state": "TX", "zip": "75201"},
            {"address": "741 Ash Boulevard", "city": "San Jose", "state": "CA", "zip": "95101"}
        ]
    
    def luhn_checksum(self, card_number):
        """Calculate Luhn checksum for card validation"""
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10
    
    def generate_valid_card_number(self, bin_code):
        """Generate a valid card number using Luhn algorithm"""
        # Generate random digits for the middle part
        if bin_code.startswith('3'):  # American Express (15 digits)
            middle_digits = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            partial_number = bin_code + middle_digits
        else:  # Visa/Mastercard/Discover (16 digits)
            middle_digits = ''.join([str(random.randint(0, 9)) for _ in range(9)])
            partial_number = bin_code + middle_digits
        
        # Calculate check digit
        check_digit = (10 - self.luhn_checksum(partial_number + '0')) % 10
        return partial_number + str(check_digit)
    
    def generate_realistic_expiry(self):
        """Generate realistic expiry date (1-5 years from now)"""
        current_date = datetime.now()
        future_date = current_date + timedelta(days=random.randint(365, 1825))  # 1-5 years
        return f"{future_date.month:02d}/{str(future_date.year)[2:]}"
    
    def generate_cvv(self, card_number):
        """Generate CVV based on card type"""
        if card_number.startswith('3'):  # American Express
            return str(random.randint(1000, 9999))  # 4-digit CVV
        else:
            return str(random.randint(100, 999))    # 3-digit CVV
    
    def generate_realistic_balance(self, card_level):
        """Generate realistic balance based on card level"""
        balance_ranges = {
            "Standard": (500, 2500),
            "Classic": (1000, 5000),
            "Gold": (2500, 10000),
            "Platinum": (5000, 25000),
            "Premium": (10000, 50000)
        }
        min_bal, max_bal = balance_ranges.get(card_level, (500, 2500))
        return round(random.uniform(min_bal, max_bal), 2)
    
    def calculate_realistic_price(self, balance, card_level):
        """Calculate realistic price based on balance and card level"""
        base_percentage = {
            "Standard": 0.02,    # 2%
            "Classic": 0.025,    # 2.5%
            "Gold": 0.03,        # 3%
            "Platinum": 0.035,   # 3.5%
            "Premium": 0.04      # 4%
        }
        
        percentage = base_percentage.get(card_level, 0.02)
        base_price = balance * percentage
        
        # Add some randomness
        variation = random.uniform(0.8, 1.2)
        final_price = base_price * variation
        
        # Minimum price constraints
        min_price = 25 if card_level in ["Premium", "Platinum"] else 15
        return max(round(final_price, 2), min_price)
    
    def generate_enhanced_card(self):
        """Generate a single enhanced card with realistic data"""
        # Select random BIN
        bin_code = random.choice(list(self.enhanced_bins.keys()))
        bin_info = self.enhanced_bins[bin_code]
        
        # Generate card details
        card_number = self.generate_valid_card_number(bin_code)
        expiry = self.generate_realistic_expiry()
        cvv = self.generate_cvv(card_number)
        
        # Select realistic personal data
        cardholder_name = random.choice(self.realistic_names)
        address_info = random.choice(self.realistic_addresses)
        
        # Generate financial data
        balance = self.generate_realistic_balance(bin_info["level"])
        price = self.calculate_realistic_price(balance, bin_info["level"])
        
        return {
            "card_number": card_number,
            "expiry": expiry,
            "cvv": cvv,
            "cardholder_name": cardholder_name,
            "bin": bin_code,
            "issuer": bin_info["issuer"],
            "card_type": bin_info["type"],
            "level": bin_info["level"],
            "country": bin_info["country"],
            "address": address_info["address"],
            "city": address_info["city"],
            "state": address_info["state"],
            "zip_code": address_info["zip"],
            "balance": balance,
            "price": price,
            "is_available": True,
            "validity_score": random.randint(75, 95)  # High validity for enhanced cards
        }
    
    def validate_card_number(self, card_number):
        """Validate card number using Luhn algorithm"""
        return self.luhn_checksum(card_number) == 0
    
    def get_card_brand(self, card_number):
        """Determine card brand from card number"""
        if card_number.startswith('4'):
            return 'Visa'
        elif card_number.startswith(('51', '52', '53', '54', '55')):
            return 'Mastercard'
        elif card_number.startswith(('34', '37')):
            return 'American Express'
        elif card_number.startswith('6'):
            return 'Discover'
        else:
            return 'Unknown'

# Global instance
enhanced_generator = AdvancedCardGenerator()
