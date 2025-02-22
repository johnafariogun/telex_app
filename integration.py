import os
import asyncio
import httpx
import uvicorn
import psycopg2
import psycopg2.pool
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Load environment variables
load_dotenv()

# FastAPI app setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Database connection pool
DB_POOL = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    dbname=os.getenv("DB_NAME", "file_monitor"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "yourpassword"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
)

# Models
class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str

class LogPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]

# Utility function to get a database connection
def get_db_connection():
    try:
        return DB_POOL.getconn()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# Home route
@app.get("/")
def root():
    return {"message": "File Monitor API is running!"}

# Integration metadata
@app.get("/integration.json")
def get_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "data": {
            "date": {"created_at": "2025-02-22", "updated_at": "2025-02-22"},
            "descriptions": {
                "app_name": "DELETE MONITOR",
                "app_description": "Monitors file deletions using auditd, logs events, and sends Telex alerts.",
                "app_logo": "https://www.pngegg.com/en/png-biocr",
                "app_url": base_url,
                "background_color": "#fff",
            },
            "is_active": True,
            "integration_type": "interval",
            "integration_category": "Monitoring & Logging",
            "key_features": [
                "Monitors a specified directory on a server",
                "Sends alerts to Telex on file deletion events",
                "Captures the user who deleted the file",
            ],
            "author": "John Tolulope Afariogun",
            "settings": [
                {"label": "interval", "type": "text", "required": True, "default": "* * * * *"},
                {"label": "site", "type": "text", "required": True, "default": f"{base_url}/logs"},
            ],
            "target_url": base_url,
            "tick_url": f"{base_url}/send-logs",
        }
    }

# Fetch logs from an external source
async def fetch_logs(site: str) -> List[dict]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{site}/{datetime.today().strftime('%Y-%m-%d')}", timeout=10)
            response.raise_for_status()
            return response.json().get("logs", [])
    except Exception as e:
        return [{"error": f"Failed to fetch logs from {site}: {str(e)}"}]

# Send logs to Telex
def send_to_telex(message: str, webhook_url: str):
    try:
        payload = {
            "message": message,
            "event_name": "❌ DELETE LOGS",
            "status": "success" if message else "error",
            "username": "DELETE LOGGER",
        }
        httpx.post(webhook_url, json=payload, timeout=5).raise_for_status()
    except httpx.HTTPError as e:
        print(f"❌ Failed to send to Telex: {e}")

# Background task for sending logs
async def send_logs_task(payload: LogPayload):
    site = [s.default for s in payload.settings if s.label.startswith("site")]
    print(site)
    logs = await asyncio.run(fetch_logs(site[0])
    send_to_telex(logs, payload.return_url)

# Trigger log sending
@app.post("/send-logs", status_code=202)
def trigger_log_sending(payload: LogPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_logs_task, payload)
    return {"status": "accepted"}

# Get all logs
@app.get("/logs")
def get_all_logs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, file_path, deleted_by FROM file_deletions ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        cursor.close()
        DB_POOL.putconn(conn)
        return {"logs": [{"id": log[0], "timestamp": log[1], "file_path": log[2], "deleted_by": log[3]} for log in logs]}
    except Exception as e:
        return {"error": str(e)}

# Get logs by date
@app.get("/logs/{date}")
def get_logs_by_date(date: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, file_path, deleted_by FROM file_deletions WHERE DATE(timestamp) = %s ORDER BY timestamp DESC", (date,))
        logs = cursor.fetchall()
        cursor.close()
        DB_POOL.putconn(conn)
        return {"logs": [{"id": log[0], "timestamp": log[1], "file_path": log[2], "deleted_by": log[3]} for log in logs]}
    except Exception as e:
        return {"error": str(e)}

# Run FastAPI
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

