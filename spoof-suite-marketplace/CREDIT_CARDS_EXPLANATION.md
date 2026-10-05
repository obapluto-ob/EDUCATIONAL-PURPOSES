# Credit Cards System Explanation

## 📁 File Structure Overview

The credit cards system is built around `app/routes/credit_cards.py` which handles all credit/debit card operations.

## 🔧 How credit_cards.py Works

### **1. Blueprint Setup**
```python
cards_bp = Blueprint('credit_cards', __name__, url_prefix='/credit-cards')
```
- Creates a Flask Blueprint for organizing routes
- All routes are prefixed with `/credit-cards/`

### **2. Main Routes & Functions**

#### **A. Buy Card Route (`/buy`)**
```python
@cards_bp.route('/buy', methods=['POST'])
def buy_card():
```
**Purpose**: Handles direct card purchases
**Process**:
1. Checks user wallet balance (minimum $50)
2. Finds card by card number
3. Validates sufficient funds
4. Deducts price from wallet
5. Adds card to purchased list in session
6. Redirects with success message

#### **B. Add to Cart Route (`/cart/add`)**
```python
@cards_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
```
**Purpose**: Adds cards to shopping cart
**Process**:
1. Gets card details from form
2. Finds card in database
3. Adds to session cart
4. Redirects back to card listing

#### **C. Card Display Routes**

**Credit Cards Home (`/`)**:
- Displays paginated credit cards
- Handles BIN search functionality
- Shows user profile and cart info

**Debit Cards (`/debit`)**:
- Similar to credit cards but filters for debit type
- Same pagination and search features

**History (`/history`)**:
- Shows purchased cards using Purchase model
- Displays full card details including Phone, SSN, DOB

### **3. Data Flow**

#### **Card Generation**:
```
realistic_card_generator.py → CreditCard model → Database
```

#### **Purchase Flow**:
```
User clicks Buy → buy_card() → Wallet check → Purchase → Session update
```

#### **Cart Flow**:
```
User clicks Add → add_to_cart() → Session cart → view_cart()
```

### **4. Database Models Used**

#### **CreditCard Model**:
- `card_number`: Primary identifier
- `price`: Card cost
- `balance`: Available balance (for verified cards)
- `note`: 'verified' or 'not checked'
- `validity_percent`: 55%, 60%, 80%, 45%, 35%
- `phone`, `ssn`, `dob`: Personal data
- `is_available`: Purchase status

#### **Purchase Model**:
- `user_id`: Buyer
- `card_id`: Purchased card
- `purchase_price`: Amount paid
- `purchased_at`: Timestamp

### **5. Session Management**

#### **Cart System**:
```python
session['cart'] = [
    {
        'card_number': '4111111111111111',
        'card_type': 'credit',
        'quantity': 1,
        'price': 25.67
    }
]
```

#### **Purchase Tracking**:
```python
session['purchased_cards'] = ['4111111111111111', '5555555555554444']
```

### **6. Security & Validation**

#### **Access Control**:
- All routes require `@login_required`
- User authentication via Flask-Login

#### **Data Validation**:
- Wallet balance checks
- Card existence validation
- Price verification

#### **Data Privacy**:
- Phone numbers hidden until purchase
- SSN/DOB shown only for verified cards
- Unverified cards show "None" for sensitive data

### **7. Template Integration**

#### **Templates Used**:
- `credit_cards/credit.html`: Main credit card listing
- `credit_cards/debit.html`: Debit card listing  
- `credit_cards/credit_history.html`: Purchase history
- `cart.html`: Shopping cart view

#### **Data Passed to Templates**:
```python
{
    'cards': paginated_cards,
    'user_profile': user_info,
    'cart_count': cart_items_count,
    'purchased_cards': purchased_list,
    'page': current_page,
    'total_pages': pagination_info
}
```

### **8. Key Features**

#### **Pricing System**:
- **Verified Cards**: 2% of balance ($99-$9999)
- **80% Valid**: $45-$85
- **60% Valid**: $25-$55  
- **55% Valid**: $15-$35
- **45% Valid**: $8-$18
- **35% Valid**: $3-$12

#### **Card Types**:
- Credit cards (`card_type='credit'`)
- Debit cards (`card_type='debit'`)

#### **Verification Levels**:
- **Verified**: Show balance, real personal data
- **Unverified**: Show validity %, hide personal data

### **9. Performance Optimizations**

#### **Database Queries**:
- Filtered queries by `is_available=True`
- Pagination to limit results
- Indexed searches by card_number

#### **Session Efficiency**:
- Cart stored in session (not database)
- Minimal database hits for cart operations

### **10. Error Handling**

#### **Common Scenarios**:
- Insufficient wallet balance
- Card not found
- Invalid card numbers
- Session timeouts

#### **User Feedback**:
- Flash messages for all operations
- Redirect to appropriate pages
- Clear error descriptions

## 🚀 System Flow Summary

1. **Card Generation**: Realistic cards created with proper BIN info
2. **Display**: Cards shown with pricing and validity info
3. **Shopping**: Users add cards to cart or buy directly
4. **Purchase**: Wallet deduction and card unlocking
5. **History**: Full card details available post-purchase

This system provides a complete e-commerce experience for credit/debit card sales with proper security, validation, and user experience features.
