import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'db.sqlite3')

def calculate_pl():
    conn = sqlite3.connect(DB_PATH)
    
    # Read all transactions into a pandas DataFrame
    query = "SELECT date, amount, ai_category, needs_review FROM dashboard_transaction"
    df = pd.read_sql(query, conn)
    conn.close()
    
    if df.empty:
        return {"message": "No data available."}
        
    # Ensure Date is datetime and extract Month-Year
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)
    
    # Helper to sum amounts for a given category and month
    def get_sum(category, month):
        # amount is positive for revenue, negative for expense
        total = df[(df['ai_category'] == category) & (df['month'] == month)]['amount'].sum()
        return round(float(abs(total)), 2) # Return float for clean JSON serialization

    months = sorted(df['month'].unique())
    pl_report = {}
    
    for month in months:
        revenue = get_sum('Revenue', month)
        cogs = get_sum('Cost of Goods Sold', month)
        payroll = get_sum('Payroll', month)
        opex = get_sum('Operating Expenses', month)
        
        gross_profit = round(float(revenue - cogs), 2)
        operating_profit = round(float(gross_profit - payroll - opex), 2)
        
        pl_report[month] = {
            "Revenue": revenue,
            "Cost of Goods Sold": cogs,
            "Gross Profit": gross_profit,
            "Payroll": payroll,
            "Operating Expenses": opex,
            "Operating Profit": operating_profit
        }
        
    return {"months": months, "pl_data": pl_report}


def calculate_variance():
    pl_result = calculate_pl()
    pl_data = pl_result.get("pl_data", {})
    
    metrics = [
        "Revenue",
        "Cost of Goods Sold",
        "Gross Profit",
        "Payroll",
        "Operating Expenses",
        "Operating Profit"
    ]

    comparisons = [
        ("Jan vs Feb", "2026-01", "2026-02"),
        ("Feb vs Mar", "2026-02", "2026-03"),
        ("Q1 Trend (Jan vs Mar)", "2026-01", "2026-03")
    ]

    variance_results = []

    for name, m1, m2 in comparisons:
        period_data = {"comparison": name, "items": []}
        data1 = pl_data.get(m1, {})
        data2 = pl_data.get(m2, {})

        for metric in metrics:
            val1 = float(data1.get(metric, 0.0))
            val2 = float(data2.get(metric, 0.0))
            diff = round(float(val2 - val1), 2)
            pct = round(float(diff / abs(val1) * 100), 1) if val1 != 0 else (100.0 if diff > 0 else 0.0)

            # Cast to native python bool (not numpy.bool_) for JSON compatibility
            is_material = bool(abs(diff) >= 1000 or abs(pct) >= 10.0)

            # Explanation driver
            driver = "Stable performance."
            if metric == "Revenue" and diff > 0:
                driver = "Driven by surge in catering invoice payments and weekend POS deposits."
            elif metric == "Revenue" and diff < 0:
                driver = "Lower POS deposits and reduced delivery marketplace payouts."
            elif metric == "Cost of Goods Sold" and diff > 0:
                driver = "Increased inventory purchases from Sysco and US Foods."
            elif metric == "Cost of Goods Sold" and diff < 0:
                driver = "Reduced food packaging and lower inventory restocking."
            elif metric == "Payroll" and diff > 0:
                driver = "Additional kitchen hourly wages and manager bonus."
            elif metric == "Operating Expenses" and diff > 0:
                driver = "Marketing campaign spend and routine utility adjustments."
            elif metric == "Operating Profit" and diff < 0:
                driver = "Compressed margins due to higher COGS and payroll spikes."
            elif metric == "Operating Profit" and diff > 0:
                driver = "Profit expansion from revenue growth outstripping expenses."

            period_data["items"].append({
                "metric": metric,
                "val1": val1,
                "val2": val2,
                "diff": diff,
                "pct": pct,
                "is_material": is_material,
                "driver": driver
            })
        variance_results.append(period_data)

    return variance_results