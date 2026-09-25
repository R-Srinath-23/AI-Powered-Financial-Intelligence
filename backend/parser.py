import pandas as pd
import sqlite3
import os

# Point to the Django SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'db.sqlite3')

def parse_and_save_csv(file_path):
    # 1. Read CSV using pandas
    df = pd.read_csv(file_path)
    
    # 2. Clean the data
    # Remove $ and , from the Amount column, handle negatives correctly
    df['Amount'] = df['Amount'].replace({r'\$': '', ',': '', r'\(': '-', r'\)': ''}, regex=True)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    # Ensure date is in the correct format (YYYY-MM-DD)
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    
    # Create the needed columns matching our Django model
    # By default, AI classification is empty and needs_review is False
    df['ai_category'] = None
    df['ai_confidence'] = None
    df['needs_review'] = False
    
    # Rename columns to match Django DB table exactly
    df = df.rename(columns={
        'Transaction ID': 'transaction_id',
        'Date': 'date',
        'Description': 'description',
        'Counterparty': 'counterparty',
        'Amount': 'amount',
        'Method': 'method'
    })
    
    # 3. Save to SQLite Database
    conn = sqlite3.connect(DB_PATH)
    
    # We use 'append' to add to the existing table created by Django
    df.to_sql('dashboard_transaction', conn, if_exists='append', index=False)
    
    conn.close()
    
    return {"message": f"Successfully parsed and saved {len(df)} transactions!"}
