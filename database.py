import sqlite3
import json
from datetime import datetime
import os

class PaymentDatabase:
    def __init__(self, db_path="payment_summaries.db"):
        """Initialize the database connection and create tables if they don't exist."""
        # Delete existing database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            
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
    
    def get_all_summaries(self):
        """Retrieve all payment summaries."""
        self.cursor.execute('SELECT payment_id, analysis FROM payment_summaries')
        return [(row[0], json.loads(row[1])) for row in self.cursor.fetchall()]
    
    def close(self):
        """Close the database connection."""
        self.conn.close() 