# 💰 Finz — AI-Powered Financial Intelligence Dashboard

> A full-stack web application that ingests bank transaction data, uses Google Gemini AI to automatically categorize every transaction, generates a deterministic monthly Profit & Loss statement, and provides an AI Financial Analyst chat — built for NYC Restaurant Co.

---

## 📸 Features

| # | Feature | Description |
|---|---|---|
| 1 | 📤 **Data Ingestion** | Drag & drop bank statement CSV files for instant import |
| 2 | 🤖 **AI Categorization** | Google Gemini automatically classifies every transaction |
| 3 | 📊 **P&L Statement** | Mathematically accurate monthly Profit & Loss report |
| 4 | 🔍 **Review Queue** | Low-confidence transactions flagged for human review & approval |
| 5 | 📈 **Variance Analysis** | Month-over-month budget vs actual comparison with drivers |
| 6 | 💬 **AI Analyst Chat** | Ask natural language questions about your financials |

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Django 5.x + Django Templates |
| Styling | Tailwind CSS (CDN) + Custom CSS |
| Backend API | FastAPI + Uvicorn |
| Database | SQLite (via Django ORM) |
| AI Engine | Google Gemini API (`gemini-3.8-flash`) |
| Data Processing | Pandas + NumPy |
| Environment | Python 3.11, virtualenv |

---

## 🗂️ Project Structure

```
Finz/
├── backend/                  # FastAPI backend
│   ├── main.py               # API routes (upload, categorize, P&L, variance, chat)
│   ├── parser.py             # CSV ingestion & cleaning logic
│   ├── gemini_service.py     # Google Gemini AI categorization & chat
│   └── pl_engine.py          # Deterministic P&L & variance calculation engine
│
├── frontend/                 # Django frontend
│   ├── config/               # Django project settings & URLs
│   │   ├── settings.py
│   │   └── urls.py
│   └── dashboard/            # Main app
│       ├── models.py         # Transaction & Correction DB models
│       ├── views.py          # Page view controllers
│       ├── urls.py           # URL routing
│       └── templates/
│           └── dashboard/
│               ├── base.html         # Master layout (sidebar + header)
│               ├── upload.html       # CSV upload page
│               ├── transactions.html # Transaction table with AI badges
│               ├── pl.html           # Profit & Loss statement
│               ├── review_queue.html # Flagged transaction review
│               ├── variance.html     # Variance analysis page
│               └── chat.html         # AI Financial Analyst chat
│
├── .env                      # Secret keys (NOT committed to Git)
├── .env.example              # Template for environment variables
├── .gitignore
└── requirements.txt
```

---

## ⚙️ Local Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Finz
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
# Copy the example file
copy .env.example .env

# Open .env and add your Gemini API key
# Get a free key at: https://aistudio.google.com
GEMINI_API_KEY=your_actual_key_here
```

### 5. Set Up the Database
```bash
cd frontend
python manage.py makemigrations
python manage.py migrate
cd ..
```

---

## 🚀 Running the Application

You need **two terminals** running simultaneously.

### Terminal 1 — FastAPI Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```
API live at: `http://127.0.0.1:8000`

### Terminal 2 — Django Frontend
```bash
cd frontend
python manage.py runserver 8080
```
App live at: `http://127.0.0.1:8080`

---

## 📖 How to Use

1. **Go to** `http://127.0.0.1:8080`
2. **Upload** your bank statement CSV on the Data Ingestion page
3. **Click** `✨ Run AI Categorization` on the Transactions page
4. **Review** flagged transactions in the Review Queue
5. **View** the monthly P&L statement
6. **Analyze** month-over-month variances on the Variance Analysis page
7. **Chat** with the AI Analyst for instant financial insights

---

## 🔌 API Endpoints (FastAPI)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/api/upload` | Upload and parse a CSV file |
| `POST` | `/api/categorize` | Run Gemini AI on all uncategorized transactions |
| `GET` | `/api/pl` | Get the monthly P&L report data |
| `GET` | `/api/variance` | Get month-over-month variance analysis |
| `POST` | `/api/chat` | Send a message to the AI Financial Analyst |

Interactive API docs: `http://127.0.0.1:8000/docs`

---

## 🏷️ AI Categories

| Category | Example |
|---|---|
| `Revenue` | POS sales, delivery platform payouts |
| `Cost of Goods Sold` | Sysco food orders, beverage purchases |
| `Payroll` | ADP payroll runs, staff wages |
| `Operating Expenses` | Rent, insurance, software subscriptions |
| `Needs Review` | Loans, owner draws, tax remittances |

> Transactions with confidence below 80% are automatically **flagged for human review**.

---

## 🔒 Security Notes

- Never commit your `.env` file — it is listed in `.gitignore`
- The `SECRET_KEY` in `settings.py` should be changed before deploying to production
- Set `DEBUG = False` in production

---

## 📋 Requirements

See [`requirements.txt`](./requirements.txt) for the full list. Key packages:

- `django` — Web framework
- `fastapi` + `uvicorn` — REST API server
- `pandas` + `numpy` — Data processing
- `google-generativeai` — Gemini AI SDK
- `python-dotenv` — Environment variable management
- `python-multipart` — File upload support for FastAPI
- `requests` — HTTP calls between Django and FastAPI
- `whitenoise` — Static file serving

---

## 👤 Author

Built as part of the SWE Internship Task for **NYC Restaurant Co.**
