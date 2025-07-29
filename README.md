## 🛡️ Intrusion Detection System (IDS)

A lightweight Python-based intrusion detection system that monitors SSH login attempts via `/var/log/auth.log`, detects brute-force attacks, and sends real-time alerts to Telegram. Designed to run persistently using `nohup` for background execution.

---

### 📦 Features

- Monitors failed SSH login attempts using `watchdog`
- Detects brute-force attacks based on configurable thresholds
- Sends alerts to Telegram with detailed threat analysis
- Logs incidents to CSV for auditing
- `.env` support for dynamic configuration

---

### 🚀 Getting Started

#### 1. Install System Dependencies

Make sure `rsyslog` and `auditd` are installed and running:

```bash
sudo apt update && sudo apt install rsyslog auditd -y
sudo systemctl enable --now rsyslog auditd
```

---

#### 2. Clone the Repository

```bash
git clone https://github.com/ty-limeng/PyIDS.git
cd PyIDS
```

---

#### 3. Create `.env` File

Create a `.env` file in the root directory with the following content:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DESTINATION_IP=192.168.204.135
```

---

#### 4. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

---

#### 5. Run the Monitor Script with `nohup`

```bash
nohup python3 monitor.py > monitor.log 2>&1 &
```

> This will keep the script running in the background and log output to `monitor.log`.

---

### 🐍 Project Structure

```
├── monitor.py              # Monitors auth.log for failed login attempts
├── logs_and_alerts.py      # Handles logging and Telegram alerting
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables
└── README.md               # Project documentation
```

---

### ⚙️ Configuration

You can adjust detection thresholds in `monitor.py`:

```python
THRESHOLD = 3       # Attempts before alert
TIME_WINDOW = 60    # Time window in seconds
ALERT_WINDOW = 30   # Minimum time between alerts
```

---

### 📬 Telegram Alerts

Alerts include:
- Source IP
- Destination IP
- Username
- Number of failed attempts
- Failure reason
- Recommended actions
---

# 🛡️ Python-Based IDS (Docker Deployment)

This guide explains how to build and run the Python-Based Intrusion Detection System (IDS) using Docker and Docker Compose.

---

## ⚙️ Build Docker Image

To build the Docker image from the source code in this repository, run:

```bash
docker build --no-cache -t python-ids .
```
Or pull the prebuilt image from Docker Hub:

```bash
docker pull tybytes/pysentinel:v1.0
```
---

## 📦 Docker Compose Setup

Create a `.env` file in the root directory with the following content:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
DESTINATION_IP=192.168.204.135
```

Then use the following `docker-compose.yml` configuration:

```yaml
services:
  brute-monitor:
    image: python-ids
    network_mode: host
    restart: unless-stopped
    volumes:
      - ./data:/alerts # Either bind mount or docker volume
      - /var/log/auth.log:/var/log/auth.log:ro # Mount auth.log in read only (ro)
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
      - DESTINATION_IP=${DESTINATION_IP}
    user: "0:0" # Run in root to avoid file permission issues
```

Start the service:

```bash
docker compose up -d
```

---

## 🐚 Docker CLI Alternative

If you prefer to run the container directly using Docker CLI:

```bash
docker run -d \
  --name brute-monitor \
  --network host \
  --restart unless-stopped \
  -v $(pwd)/data:/alerts \
  -v /var/log/auth.log:/var/log/auth.log:ro \
  -e TELEGRAM_BOT_TOKEN=your_telegram_bot_token \
  -e TELEGRAM_CHAT_ID=your_telegram_chat_id \
  -e DESTINATION_IP=192.168.204.135 \
  --user 0:0 \
  python-ids
```




