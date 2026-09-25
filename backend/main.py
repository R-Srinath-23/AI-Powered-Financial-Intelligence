from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from parser import parse_and_save_csv
from gemini_service import categorize_transactions, chat_with_analyst
from pl_engine import calculate_pl, calculate_variance
from pydantic import BaseModel


app = FastAPI(title="Finz API")

# Allow Django to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Finz API is running!"}

@app.post("/api/upload")
async def upload_transactions(file: UploadFile = File(...)):
    # 1. Save the uploaded file temporarily
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 2. Parse the CSV and save to SQLite
        result = parse_and_save_csv(temp_file_path)
        
        # 3. Delete the temporary file
        os.remove(temp_file_path)
        
        return result
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return {"error": str(e)}

@app.post("/api/categorize")
def trigger_ai_categorization():
    try:
        result = categorize_transactions()
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/pl")
def get_pl_report():
    try:
        return calculate_pl()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/variance")
def get_variance_report():
    try:
        return calculate_variance()
    except Exception as e:
        return {"error": str(e)}

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
def handle_chat(payload: ChatRequest):
    try:
        reply = chat_with_analyst(payload.message)
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"Sorry, I encountered an error: {str(e)}"}

