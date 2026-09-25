import os
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Load environment variables (API Key)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

DB_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), '..', 'frontend', 'db.sqlite3'))

# Prioritize models with high quota availability and fall back automatically
MODELS = ['gemini-3.5-flash', 'gemini-3.7-flash', 'gemini-3.1-flash-lite', 'gemini-3.8-flash']

def generate_content_with_fallback(prompt: str) -> str:
    last_err = None
    for model_name in MODELS:
        try:
            m = genai.GenerativeModel(model_name)
            response = m.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            continue
    raise last_err or Exception("Failed to generate content from any Gemini model.")

def categorize_transactions():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY is not configured. Please set your GEMINI_API_KEY in Render environment variables."}
    genai.configure(api_key=api_key)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all uncategorized transactions
    cursor.execute("SELECT * FROM dashboard_transaction WHERE ai_category IS NULL")
    transactions = cursor.fetchall()
    
    if not transactions:
        return {"message": "All transactions are already categorized!"}
        
    prompt = """
    You are an expert AI accountant. Categorize the following bank transactions.
    You MUST assign one of these exact categories:
    - Revenue
    - Cost of Goods Sold
    - Payroll
    - Operating Expenses
    - Needs Review (use this for unusual things like Loans, Owner Draws, Tax remittance)

    Return the response as a pure JSON list of objects, with no markdown formatting.
    Format: [{"transaction_id": "T1001", "category": "Revenue", "confidence": 95}, ...]

    Transactions to categorize:
    """
    
    # Send transactions in batches of 50 to avoid huge prompts
    batch = []
    updated_count = 0
    
    for row in transactions:
        batch.append(f"ID: {row['transaction_id']} | Desc: {row['description']} | To/From: {row['counterparty']} | Amount: {row['amount']}")
        
        if len(batch) >= 50 or row == transactions[-1]:
            full_prompt = prompt + "\n".join(batch)
            
            try:
                # Ask Gemini with automatic fallback across models
                response_text = generate_content_with_fallback(full_prompt)
                
                # Clean up the response to just get JSON
                cleaned_json = response_text.replace('```json', '').replace('```', '').strip()
                results = json.loads(cleaned_json)
                
                # Update the database
                for res in results:
                    needs_review = True if res['category'] == 'Needs Review' or res['confidence'] < 80 else False
                    
                    cursor.execute("""
                        UPDATE dashboard_transaction 
                        SET ai_category = ?, ai_confidence = ?, needs_review = ?
                        WHERE transaction_id = ?
                    """, (res['category'], res['confidence'], needs_review, res['transaction_id']))
                
                conn.commit()
                updated_count += len(results)
                batch = [] # Reset for next batch
                
            except Exception as e:
                print(f"Error processing batch: {e}")
                
    conn.close()
    return {"message": f"Successfully categorized {updated_count} transactions using AI!"}

def chat_with_analyst(user_message: str):
    import sqlite3
    import pandas as pd
    from pl_engine import calculate_pl, calculate_variance

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: **GEMINI_API_KEY** is not configured. Please add it to your Render environment variables."

    genai.configure(api_key=api_key)

    pl_summary = calculate_pl()
    variance_summary = calculate_variance()

    try:
        conn = sqlite3.connect(DB_PATH)
        flagged_df = pd.read_sql("SELECT transaction_id, date, description, counterparty, amount, ai_category FROM dashboard_transaction WHERE needs_review = 1 LIMIT 5", conn)
        large_txns = pd.read_sql("SELECT transaction_id, date, description, counterparty, amount, ai_category FROM dashboard_transaction ORDER BY ABS(amount) DESC LIMIT 5", conn)
        conn.close()
        flagged_data = flagged_df.to_dict(orient='records')
        large_data = large_txns.to_dict(orient='records')
    except Exception:
        flagged_data = []
        large_data = []

    context_prompt = f"""You are the Senior Financial AI Analyst for NYC Restaurant Co. (Finz).
Answer the user's question concisely using ONLY the real financial data below. Cite specific figures.

P&L SUMMARY: {pl_summary.get('pl_data', {})}
VARIANCE: {variance_summary}
FLAGGED TRANSACTIONS: {flagged_data}
TOP TRANSACTIONS: {large_data}

Question: {user_message}
Answer concisely with key figures bolded using **bold**:"""

    try:
        reply = generate_content_with_fallback(context_prompt)
        return reply
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
