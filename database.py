import sqlite3
import json
from datetime import datetime
import os

class PaymentDatabase:
    def __init__(self, db_path="payment_summaries.db"):
        """Initialize the database connection and create tables if they don't exist."""
        # Delete existing database if it exists
        # if os.path.exists(db_path):
        #     os.remove(db_path)
            
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_id INTEGER,
                original_payment JSON,
                analysis JSON,
                price_value TEXT,
                price_currency TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def store_payment_summary(self, payment_id, original_payment, summary):
        """Store a payment summary in the database."""
        if isinstance(summary, str):
            summary = json.loads(summary)
        # Extract price information from the summary
        price_value = summary.get('price', {}).get('value', '')
        price_currency = summary.get('price', {}).get('currency', '')
        
        self.cursor.execute('''
            INSERT INTO payment_summaries (payment_id, original_payment, analysis, price_value, price_currency)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            payment_id,
            json.dumps(original_payment),
            json.dumps(summary),
            price_value,
            price_currency
        ))
        self.conn.commit()
    
    def get_payment_summary(self, payment_id):
        """Retrieve a payment summary by payment ID."""
        self.cursor.execute('''
            SELECT analysis FROM payment_summaries 
            WHERE payment_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (payment_id,))
        result = self.cursor.fetchone()
        return json.loads(result[0]) if result else None
    
    def get_payment_details(self, payment_id):
        """Retrieve both original payment and summary for a given payment ID.
        
        Args:
            payment_id: The ID of the payment to retrieve
            
        Returns:
            tuple: (original_payment, summary) or (None, None) if not found
        """
        self.cursor.execute('''
            SELECT original_payment, analysis 
            FROM payment_summaries 
            WHERE payment_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (payment_id,))
        result = self.cursor.fetchone()
        
        if result:
            return json.loads(result[0]), json.loads(result[1])
        return None, None
    
    def get_all_summaries(self):
        """Retrieve all payment summaries."""
        self.cursor.execute('SELECT payment_id, analysis FROM payment_summaries')
        return [(row[0], json.loads(row[1])) for row in self.cursor.fetchall()]
    
    def close(self):
        """Close the database connection."""
        self.conn.close()

class ActivityDatabase:
    def __init__(self, db_path="activities.db"):
        """Initialize the database connection and create tables if they don't exist."""
        # if os.path.exists(db_path):
        #     os.remove(db_path)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                company TEXT,
                product TEXT,
                discount_amount REAL,
                is_free BOOLEAN,
                location TEXT,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                status TEXT CHECK(status IN ('active', 'used', 'timeout')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def add_activity(self, user_id, company, product, discount_amount, is_free, location, start_date, end_date):
        """Add a new activity/offer to the database."""
        self.cursor.execute('''
            INSERT INTO activities (
                user_id, company, product, discount_amount, is_free, 
                location, start_date, end_date, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
        ''', (
            user_id, company, product, discount_amount, is_free,
            location, start_date, end_date
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_activity_status(self, activity_id, new_status):
        """Update the status of an activity."""
        if new_status not in ['active', 'used', 'timeout']:
            raise ValueError("Status must be one of: active, used, timeout")
            
        self.cursor.execute('''
            UPDATE activities 
            SET status = ? 
            WHERE id = ?
        ''', (new_status, activity_id))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_latest_activity(self, user_id):
        """Get the most recent active activity for a user."""
        self.cursor.execute('''
            SELECT * FROM activities 
            WHERE user_id = ? AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        ''', (user_id,))
        return self._row_to_dict(self.cursor.fetchone())
    
    def get_all_user_activities(self, user_id):
        """Get all activities for a user."""
        self.cursor.execute('''
            SELECT * FROM activities 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def _row_to_dict(self, row):
        """Convert a database row to a dictionary."""
        if row is None:
            return None
            
        return {
            'id': row[0],
            'user_id': row[1],
            'company': row[2],
            'product': row[3],
            'discount_amount': row[4],
            'is_free': bool(row[5]),
            'location': row[6],
            'start_date': row[7],
            'end_date': row[8],
            'status': row[9],
            'created_at': row[10]
        }
    
    def close(self):
        """Close the database connection."""
        self.conn.close() 


