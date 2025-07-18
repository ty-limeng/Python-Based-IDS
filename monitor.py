import re
import time
import collections
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logs_and_alerts import alert 
import os 

# Define regex to match failed login attempts
FAILED_LOGIN_REGEX = re.compile(r'Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+)')

# Dictionary to store failed attempts (now tracks by both IP and username)
failed_attempts = collections.defaultdict(lambda: collections.defaultdict(lambda: {"count": 0, "last_attempt": 0, "last_alert_time": 0}))

# Threshold settings
THRESHOLD = 3  # Number of attempts before triggering an alert
TIME_WINDOW = 60  # Time window in seconds
ALERT_WINDOW = 30  # Minimum time between alerts per user/IP

def process_line(line):
    match = FAILED_LOGIN_REGEX.search(line)
    if match:
        username, ip_address = match.groups()
        current_time = time.time()

        # Reset count if outside the time window
        if (current_time - failed_attempts[ip_address][username]["last_attempt"]) > TIME_WINDOW:
            failed_attempts[ip_address][username]["count"] = 1
        else:
            failed_attempts[ip_address][username]["count"] += 1
        
        failed_attempts[ip_address][username]["last_attempt"] = current_time

        # Check if threshold exceeded and if an alert should be sent
        if failed_attempts[ip_address][username]["count"] >= THRESHOLD:
            last_alert_time = failed_attempts[ip_address][username]["last_alert_time"]
            
            if (current_time - last_alert_time) >= ALERT_WINDOW:
                print(f"[ALERT] Possible Brute Force: IP {ip_address} (User: {username})")

                # Determine failure reason
                failure_reason = "Unknown"
                if "Invalid user" in line:
                    failure_reason = "Invalid Username"
                elif "Failed password" in line:
                    failure_reason = "Incorrect Password"

                # Send alert to Telegram
                alert(
                    source_ip=ip_address,
                    destination_ip=os.getenv("DESTINATION_IP", "No IP were set"), # Config the IP in the .env file.
                    username=username,
                    failed_attempts=failed_attempts[ip_address][username]["count"],
                    failure_reason=failure_reason
                )
                
                # Update the last alert time
                failed_attempts[ip_address][username]["last_alert_time"] = current_time

class AuthLogHandler(FileSystemEventHandler):
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = open(filepath, 'r')
        self.file.seek(0, 2)  # Move to the end of file

    def on_modified(self, event):
        if event.src_path == self.filepath:
            for line in self.file:
                process_line(line.strip())

def start_monitoring(filepath="/var/log/auth.log"):
    event_handler = AuthLogHandler(filepath)
    observer = Observer()
    observer.schedule(event_handler, path=filepath, recursive=False)
    observer.start()
    print("[INFO] Monitoring auth.log for brute-force attempts...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitoring()
