#!/usr/bin/env python3
"""
Daily Card Generation System - Just like Plaid and Fullz
Generates cards once per day and saves to database
"""

import os
import json
import random
from datetime import date, datetime
from app import create_app
from app.models import CreditCard, db
from app.utils.realistic_card_generator import generate_realistic_card

def get_system_mood():
    """Determine system mood based on various factors"""
    current_hour = datetime.now().hour
    day_of_week = datetime.now().weekday()  # 0=Monday, 6=Sunday

    # Base mood factors
    mood_score = 50  # Neutral starting point

    # Time-based mood
    if 6 <= current_hour <= 10:  # Morning rush
        mood_score += 20
    elif 12 <= current_hour <= 14:  # Lunch time
        mood_score += 15
    elif 18 <= current_hour <= 22:  # Evening peak
        mood_score += 25
    elif 0 <= current_hour <= 6:  # Late night/early morning
        mood_score -= 10

    # Day-based mood
    if day_of_week in [0, 1]:  # Monday, Tuesday - high activity
        mood_score += 15
    elif day_of_week in [4, 5]:  # Friday, Saturday - weekend prep
        mood_score += 20
    elif day_of_week == 6:  # Sunday - lower activity
        mood_score -= 5

    # Random factor for unpredictability
    random_factor = random.randint(-15, 25)
    mood_score += random_factor

    # Ensure mood stays within reasonable bounds
    mood_score = max(10, min(100, mood_score))

    return mood_score

def calculate_cards_to_generate(mood_score):
    """Calculate how many cards to generate based on mood"""
    min_cards = 687
    max_cards = 2587

    # Convert mood (0-100) to card range
    mood_ratio = mood_score / 100.0
    card_range = max_cards - min_cards
    cards_to_generate = min_cards + int(card_range * mood_ratio)

    # Add some randomness within the mood-based range
    variance = int(cards_to_generate * 0.1)  # 10% variance
    cards_to_generate += random.randint(-variance, variance)

    # Ensure within bounds
    cards_to_generate = max(min_cards, min(max_cards, cards_to_generate))

    return cards_to_generate

def determine_card_split(total_cards):
    """Determine credit/debit split based on market trends"""
    # Base split: 60% credit, 40% debit (credit cards more popular)
    base_credit_ratio = 0.60

    # Add some daily variation
    daily_variation = random.uniform(-0.15, 0.15)  # ±15% variation
    credit_ratio = max(0.45, min(0.75, base_credit_ratio + daily_variation))

    credit_cards = int(total_cards * credit_ratio)
    debit_cards = total_cards - credit_cards

    return credit_cards, debit_cards

def map_card_fields(card_data):
    """Map generator fields to database model fields"""
    mapped_data = {}

    # Direct field mappings
    field_mapping = {
        'card_number': 'card_number',
        'cvv': 'cvv',
        'expiry': 'expiry',
        'bank': 'bank',
        'country': 'country',
        'state': 'state',
        'city': 'city',
        'address': 'address',
        'phone': 'phone',
        'email': 'email',
        'email_pass': 'email_pass',
        'ssn': 'ssn',
        'dob': 'dob',
        'brand': 'brand',
        'level': 'level',
        'prepaid': 'prepaid',
        'country_flag': 'country_flag',
        'note': 'note',
        'balance': 'balance',
        'price': 'price',
        'validity_percent': 'validity_percent'
    }

    # Apply direct mappings
    for gen_field, db_field in field_mapping.items():
        if gen_field in card_data:
            mapped_data[db_field] = card_data[gen_field]

    # Special field mappings
    if 'cardholder_name' in card_data:
        mapped_data['holder_name'] = card_data['cardholder_name']
    if 'bin' in card_data:
        mapped_data['bin_code'] = card_data['bin']
    if 'zip' in card_data:
        mapped_data['zip_code'] = card_data['zip']
    if 'is_verified' in card_data:
        mapped_data['is_verified'] = bool(card_data['is_verified'])

    # Set default values
    mapped_data['is_available'] = True
    mapped_data['user_id'] = None

    # Handle datetime
    if 'created_at' in card_data:
        if isinstance(card_data['created_at'], str):
            mapped_data['created_at'] = datetime.now()
        else:
            mapped_data['created_at'] = card_data['created_at']
    else:
        mapped_data['created_at'] = datetime.now()

    return mapped_data

def get_daily_cards():
    """Get daily generated cards - same pattern as plaid and fullz"""
    today = date.today().isoformat()
    cache_file = f"data/daily_cards_{today}.json"
    
    # If today's cards already exist, return count from database
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            daily_data = json.load(f)
        
        # Return the count that was generated today
        return {
            'generated_today': daily_data.get('cards_generated', 0),
            'mood': daily_data.get('mood', 50),
            'credit_count': daily_data.get('credit_count', 0),
            'debit_count': daily_data.get('debit_count', 0),
            'generation_time': daily_data.get('generation_time', today)
        }
    
    # Generate new cards for today
    return generate_daily_cards()

def generate_daily_cards():
    """Generate cards for today based on system mood"""
    app = create_app()
    with app.app_context():
        today = date.today().isoformat()
        cache_file = f"data/daily_cards_{today}.json"
        
        print(f"🎯 Daily Card Generation - {today}")
        print("=" * 50)
        
        # Get system mood and calculate cards to generate
        mood_score = get_system_mood()
        total_cards = calculate_cards_to_generate(mood_score)
        credit_count, debit_count = determine_card_split(total_cards)
        
        print(f"📊 System Mood: {mood_score}/100")
        print(f"🎲 Target Cards: {total_cards}")
        print(f"💳 Credit Cards: {credit_count}")
        print(f"💰 Debit Cards: {debit_count}")
        print("-" * 50)
        
        # Get current database state
        before_total = CreditCard.query.count()
        before_credit = CreditCard.query.filter_by(card_type='credit').count()
        before_debit = CreditCard.query.filter_by(card_type='debit').count()
        
        print(f"📊 Current Database:")
        print(f"   Total: {before_total}")
        print(f"   Credit: {before_credit}")
        print(f"   Debit: {before_debit}")
        
        generated_count = 0
        duplicate_count = 0
        error_count = 0
        
        # Generate credit cards
        print(f"\n🔄 Generating {credit_count} Credit Cards...")
        for i in range(credit_count):
            try:
                raw_card_data = generate_realistic_card()
                card_data = map_card_fields(raw_card_data)
                card_data['card_type'] = 'credit'
                
                # Check for duplicates
                existing_card = CreditCard.query.filter_by(card_number=card_data['card_number']).first()
                if existing_card:
                    duplicate_count += 1
                    continue
                
                # Create new card
                new_card = CreditCard(**card_data)
                db.session.add(new_card)
                generated_count += 1
                
                if (i + 1) % 100 == 0:
                    print(f"   ✓ Generated {i + 1}/{credit_count} credit cards")
                    
            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    print(f"   ❌ Error generating credit card {i + 1}: {str(e)}")
                continue
        
        # Generate debit cards
        print(f"🔄 Generating {debit_count} Debit Cards...")
        for i in range(debit_count):
            try:
                raw_card_data = generate_realistic_card()
                card_data = map_card_fields(raw_card_data)
                card_data['card_type'] = 'debit'
                
                # Check for duplicates
                existing_card = CreditCard.query.filter_by(card_number=card_data['card_number']).first()
                if existing_card:
                    duplicate_count += 1
                    continue
                
                # Create new card
                new_card = CreditCard(**card_data)
                db.session.add(new_card)
                generated_count += 1
                
                if (i + 1) % 100 == 0:
                    print(f"   ✓ Generated {i + 1}/{debit_count} debit cards")
                    
            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    print(f"   ❌ Error generating debit card {i + 1}: {str(e)}")
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            
            # Get final counts
            after_total = CreditCard.query.count()
            after_credit = CreditCard.query.filter_by(card_type='credit').count()
            after_debit = CreditCard.query.filter_by(card_type='debit').count()
            
            print(f"\n✅ Daily Generation Complete!")
            print(f"📈 Successfully generated: {generated_count} cards")
            print(f"🔄 Duplicates skipped: {duplicate_count}")
            print(f"❌ Errors encountered: {error_count}")
            print(f"📊 Final Database Totals:")
            print(f"   Total: {after_total} (+{after_total - before_total})")
            print(f"   💳 Credit: {after_credit} (+{after_credit - before_credit})")
            print(f"   💰 Debit: {after_debit} (+{after_debit - before_debit})")
            
            # Save daily generation data to cache file (like plaid/fullz)
            daily_data = {
                'date': today,
                'mood': mood_score,
                'target_cards': total_cards,
                'cards_generated': generated_count,
                'credit_count': after_credit - before_credit,
                'debit_count': after_debit - before_debit,
                'duplicates_skipped': duplicate_count,
                'errors': error_count,
                'generation_time': datetime.now().isoformat(),
                'database_before': {
                    'total': before_total,
                    'credit': before_credit,
                    'debit': before_debit
                },
                'database_after': {
                    'total': after_total,
                    'credit': after_credit,
                    'debit': after_debit
                }
            }
            
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            
            # Save to cache file
            with open(cache_file, 'w') as f:
                json.dump(daily_data, f, indent=2)
            
            print(f"💾 Daily data saved to: {cache_file}")
            
            return {
                'generated_today': generated_count,
                'mood': mood_score,
                'credit_count': after_credit - before_credit,
                'debit_count': after_debit - before_debit,
                'generation_time': today
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing cards to database: {str(e)}")
            return {
                'generated_today': 0,
                'mood': mood_score,
                'credit_count': 0,
                'debit_count': 0,
                'generation_time': today,
                'error': str(e)
            }

def get_daily_card_stats():
    """Get today's card generation statistics"""
    today = date.today().isoformat()
    cache_file = f"data/daily_cards_{today}.json"
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    return {
        'date': today,
        'cards_generated': 0,
        'mood': 0,
        'status': 'not_generated_yet'
    }

def manual_daily_generation():
    """Manually trigger daily generation"""
    print("🔧 Manual Daily Card Generation Triggered")
    return generate_daily_cards()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "manual":
            manual_daily_generation()
        elif sys.argv[1] == "stats":
            stats = get_daily_card_stats()
            print(f"📊 Today's Card Generation Stats:")
            print(f"   Date: {stats.get('date', 'N/A')}")
            print(f"   Mood: {stats.get('mood', 0)}/100")
            print(f"   Generated: {stats.get('cards_generated', 0)} cards")
            print(f"   Credit: {stats.get('credit_count', 0)}")
            print(f"   Debit: {stats.get('debit_count', 0)}")
        elif sys.argv[1] == "check":
            daily_info = get_daily_cards()
            print(f"📊 Daily Card System Status:")
            print(f"   Generated Today: {daily_info['generated_today']} cards")
            print(f"   System Mood: {daily_info['mood']}/100")
        else:
            print("Usage: python daily_card_system.py [manual|stats|check]")
    else:
        # Default: check if today's cards exist, if not generate them
        daily_info = get_daily_cards()
        print(f"✅ Daily card system ready")
        print(f"📊 Today's cards: {daily_info['generated_today']}")
