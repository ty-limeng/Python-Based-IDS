import requests
import json
import os
import csv
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CASE_ID_FILE = "case_id.json"  # File to store the last case ID


def get_next_case_id():
    """Get next case ID from CSV or start at 1 if file doesn't exist."""
    try:
        with open('alerts.csv', 'r') as f:
            last_case = max(int(row['case_id']) for row in csv.DictReader(f))
            return last_case + 1
    except (FileNotFoundError, ValueError):
        return 1  # Default if file doesn't exist or is empty


def log_alert(case_id, source_ip, dest_ip, user, attempts, reason):
    """Log security alerts to CSV with case ID."""
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "case_id": case_id,
        "source_ip": source_ip,
        "dest_ip": dest_ip,
        "user": user,
        "attempts": attempts,
        "reason": reason
    }
    
    with open('alerts.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if f.tell() == 0: writer.writeheader()
        writer.writerow(data)



def send_telegram_alert(case_id, source_ip, destination_ip, username, failed_attempts, failure_reason):
    """Send an intrusion alert to Telegram with an incrementing case ID."""
    
    message = f"""
[Server] Intrusion Detected

--------------------------------------
Case # {case_id} - Possible Brute Force Attempt

Source IP: {source_ip}
Destination IP: {destination_ip}
Username: {username}

Threat Analysis:

- The user "{username}" has failed to log in {failed_attempts} times within 60s.
- Failure Reason: {failure_reason}
- More than 3 failed attempts detected from {source_ip}.

Recommended Actions:

- Investigate {source_ip} for suspicious activity.
- Consider blocking the IP or enforcing additional security measures.
- Monitor further login attempts.
    """

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message.strip(),
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        message_id = response.json().get("result", {}).get("message_id")
        print(f"[INFO] Alert sent. Case ID: {case_id}, Telegram Message ID: {message_id}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to send Telegram alert: {e}")


def alert(source_ip, destination_ip, username, failed_attempts, failure_reason):
    case_id = get_next_case_id()
    log_alert(case_id, source_ip, destination_ip, username, failed_attempts, failure_reason)
    send_telegram_alert(case_id, source_ip, destination_ip, username, failed_attempts, failure_reason)

# Example usage
#send_telegram_alert("192.168.1.10", "192.168.1.1", "admin", 5, 60, "Incorrect Password")
