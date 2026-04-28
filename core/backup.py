"""Database backup: copies SQLite file and sends it to Telegram."""
import os
import shutil
import requests
from datetime import datetime
from config.settings import DATABASE_URL, TELEGRAM_BOT_TOKEN, ADMIN_CHAT_ID

DB_PATH = DATABASE_URL.replace("sqlite:///", "")
BACKUP_DIR = "data/backups"

def create_backup() -> str:
    """Copy the current database to a timestamped file, return the path."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_name = f"agent_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    shutil.copy2(DB_PATH, backup_path)
    return backup_path

def send_backup_to_telegram(backup_path: str):
    """Send the backup file to the admin's Telegram Saved Messages."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(backup_path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": ADMIN_CHAT_ID}
        response = requests.post(url, files=files, data=data)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to send backup: {response.text}")

def daily_backup():
    """Create and send a database backup. Call from scheduler or /backup command."""
    path = create_backup()
    send_backup_to_telegram(path)
    # Optional: keep only last 7 backups
    all_backups = sorted([
        os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)
    ], key=os.path.getmtime)
    for old in all_backups[:-7]:
        os.remove(old)
    return path
