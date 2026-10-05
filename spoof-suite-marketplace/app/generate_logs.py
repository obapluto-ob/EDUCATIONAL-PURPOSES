from . import create_app, db
from .models import Log
import random
from datetime import datetime

app = create_app()

def generate_daily_logs():
    log_types = ['credit', 'debit', 'plaid', 'fullz']
    for log_type in log_types:
        num_logs = random.randint(5, 20)
        for _ in range(num_logs):
            log_data = f"Sample {log_type} log generated at {datetime.utcnow()}"
            log = Log(log_type=log_type, data=log_data)
            db.session.add(log)
    db.session.commit()
    print("Daily logs generated.")

if __name__ == "__main__":
    with app.app_context():
        generate_daily_logs()
