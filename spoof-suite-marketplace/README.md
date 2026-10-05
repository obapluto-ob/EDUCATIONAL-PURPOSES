# Spoof Suite Project

A comprehensive web-based suite for managing financial data, payments, wallets, and card information.

## Features

- **Credit & Debit Card Suite** - Manage and view card data
- **Plaid Logs** - Financial account information management
- **Fullz Data** - Complete identity profiles with financial data
- **BIN Information Checker** - Bank Identification Number lookup
- **Payment System** - BTC & USDT wallet integration
- **User Authentication** - Secure registration and login
- **Dashboard** - Comprehensive overview and navigation

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd spoof_suite_project/spoof_suite_project
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your actual configuration values
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

   The application will be available at `http://127.0.0.1:5002`

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:

- `SECRET_KEY`: Your application secret key
- `MAIL_USERNAME`: Email for notifications
- `MAIL_PASSWORD`: Email password/app password
- `DATABASE_URL`: Optional database connection string. Local development defaults to SQLite. For Render, create a PostgreSQL database and set this variable to its internal connection URL in the web service's environment. The app supports Render's `postgres://` and standard `postgresql://` URL formats.

For Render deployments, install dependencies with `pip install -r requirements.txt` and run `flask db upgrade` as the service's pre-deploy command after setting `DATABASE_URL`. The PostgreSQL database must be reachable by the service for migrations to succeed.

## Project Structure

```
spoof_suite_project/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration settings
│   ├── models.py            # Database models
│   ├── routes/              # Route blueprints
│   │   ├── auth.py          # Authentication routes
│   │   ├── main.py          # Main dashboard routes
│   │   ├── credit_cards.py  # Card management
│   │   ├── plaid_logs.py    # Plaid data routes
│   │   └── ...
│   ├── templates/           # HTML templates
│   └── utils/               # Utility functions
├── data/                    # Generated data files
├── migrations/              # Database migrations
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── .env.example            # Environment variables template
```

## How to Start the Terminal

- In VS Code, press <kbd>Ctrl</kbd> + <kbd>`</kbd> to open the terminal.
- Or, click **Terminal > New Terminal**.

## Support

For help, use the "Contact Support" option in the dashboard menu.

---

*Update this README with more details about setup, usage, and features