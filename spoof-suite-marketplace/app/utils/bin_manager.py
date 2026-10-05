"""
BIN Management System for adding new BINs and generating cards
"""
import json
import os
from typing import Dict, List
from .realistic_card_generator import REAL_BINS

BIN_DATABASE_FILE = "data/custom_bins.json"

def load_custom_bins() -> Dict:
    """Load custom BINs from file"""
    if os.path.exists(BIN_DATABASE_FILE):
        try:
            with open(BIN_DATABASE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_custom_bins(bins: Dict):
    """Save custom BINs to file"""
    os.makedirs(os.path.dirname(BIN_DATABASE_FILE), exist_ok=True)
    with open(BIN_DATABASE_FILE, 'w') as f:
        json.dump(bins, f, indent=2)

def add_new_bin(bin_code: str, bank: str, card_type: str, brand: str, level: str, country: str) -> bool:
    """Add a new BIN to the system"""
    if len(bin_code) != 6 or not bin_code.isdigit():
        return False
    
    custom_bins = load_custom_bins()
    custom_bins[bin_code] = {
        "bank": bank,
        "type": card_type.lower(),
        "brand": brand.lower(),
        "level": level,
        "country": country
    }
    save_custom_bins(custom_bins)
    return True

def get_all_bins() -> Dict:
    """Get all BINs (built-in + custom)"""
    all_bins = REAL_BINS.copy()
    custom_bins = load_custom_bins()
    all_bins.update(custom_bins)
    return all_bins

def add_popular_bins():
    """Add more popular BINs to the system"""
    new_bins = {
        # More US Banks
        "476173": {"bank": "American Express", "type": "credit", "brand": "amex", "level": "Gold", "country": "USA"},
        "378282": {"bank": "American Express", "type": "credit", "brand": "amex", "level": "Platinum", "country": "USA"},
        "371449": {"bank": "American Express", "type": "credit", "brand": "amex", "level": "Corporate", "country": "USA"},
        "343434": {"bank": "American Express", "type": "credit", "brand": "amex", "level": "Business", "country": "USA"},
        
        # Discover Cards
        "601111": {"bank": "Discover", "type": "credit", "brand": "discover", "level": "Standard", "country": "USA"},
        "644564": {"bank": "Discover", "type": "credit", "brand": "discover", "level": "Cashback", "country": "USA"},
        
        # More International Banks
        "520000": {"bank": "HSBC", "type": "credit", "brand": "mastercard", "level": "World", "country": "UK"},
        "540988": {"bank": "Santander", "type": "credit", "brand": "mastercard", "level": "Gold", "country": "UK"},
        "676770": {"bank": "Maestro", "type": "debit", "brand": "maestro", "level": "Standard", "country": "UK"},
        
        # Canadian Banks
        "450875": {"bank": "BMO", "type": "credit", "brand": "visa", "level": "Platinum", "country": "Canada"},
        "540333": {"bank": "TD Canada", "type": "credit", "brand": "mastercard", "level": "Gold", "country": "Canada"},
        
        # European Banks
        "492901": {"bank": "Deutsche Bank", "type": "credit", "brand": "visa", "level": "Gold", "country": "Germany"},
        "547580": {"bank": "BNP Paribas", "type": "credit", "brand": "mastercard", "level": "World", "country": "France"},
        "450903": {"bank": "ING", "type": "credit", "brand": "visa", "level": "Classic", "country": "Netherlands"},
        
        # Australian Banks
        "450000": {"bank": "ANZ", "type": "credit", "brand": "visa", "level": "Platinum", "country": "Australia"},
        "520000": {"bank": "Commonwealth Bank", "type": "credit", "brand": "mastercard", "level": "Gold", "country": "Australia"},
        
        # Asian Banks
        "456789": {"bank": "ICBC", "type": "credit", "brand": "visa", "level": "Gold", "country": "China"},
        "540123": {"bank": "Mitsubishi UFJ", "type": "credit", "brand": "mastercard", "level": "Platinum", "country": "Japan"},
        
        # More US Regional Banks
        "414709": {"bank": "Navy Federal", "type": "credit", "brand": "visa", "level": "Platinum", "country": "USA"},
        "526214": {"bank": "USAA", "type": "credit", "brand": "mastercard", "level": "World", "country": "USA"},
        "479999": {"bank": "Credit Union", "type": "credit", "brand": "visa", "level": "Rewards", "country": "USA"},
        "542418": {"bank": "Discover Bank", "type": "debit", "brand": "mastercard", "level": "Standard", "country": "USA"},
        
        # Prepaid Cards
        "498765": {"bank": "Green Dot", "type": "debit", "brand": "visa", "level": "Prepaid", "country": "USA"},
        "527777": {"bank": "NetSpend", "type": "debit", "brand": "mastercard", "level": "Prepaid", "country": "USA"},
        
        # Business Cards
        "414720": {"bank": "Bank of America Business", "type": "credit", "brand": "visa", "level": "Business", "country": "USA"},
        "555544": {"bank": "Chase Business", "type": "credit", "brand": "mastercard", "level": "Business", "country": "USA"},
    }
    
    custom_bins = load_custom_bins()
    custom_bins.update(new_bins)
    save_custom_bins(custom_bins)
    print(f"Added {len(new_bins)} new BINs to the system!")

def list_bins_by_country(country: str = None) -> List[Dict]:
    """List BINs by country"""
    all_bins = get_all_bins()
    if country:
        return {k: v for k, v in all_bins.items() if v.get('country', '').upper() == country.upper()}
    return all_bins

def list_bins_by_brand(brand: str) -> List[Dict]:
    """List BINs by brand"""
    all_bins = get_all_bins()
    return {k: v for k, v in all_bins.items() if v.get('brand', '').lower() == brand.lower()}

def get_bin_info(bin_code: str) -> Dict:
    """Get information about a specific BIN"""
    all_bins = get_all_bins()
    return all_bins.get(bin_code, None)

if __name__ == "__main__":
    # Add popular BINs when run directly
    add_popular_bins()
    
    # Show statistics
    all_bins = get_all_bins()
    print(f"\nTotal BINs available: {len(all_bins)}")
    
    # Count by brand
    brands = {}
    countries = {}
    for bin_data in all_bins.values():
        brand = bin_data.get('brand', 'unknown')
        country = bin_data.get('country', 'unknown')
        brands[brand] = brands.get(brand, 0) + 1
        countries[country] = countries.get(country, 0) + 1
    
    print("\nBINs by Brand:")
    for brand, count in sorted(brands.items()):
        print(f"  {brand.title()}: {count}")
    
    print("\nBINs by Country:")
    for country, count in sorted(countries.items()):
        print(f"  {country}: {count}")
