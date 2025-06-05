# 🌍 **Wazobia: WhatsApp AI Translator**

> A FastAPI-based app for seamless WhatsApp message translation between **English**, **Igbo**, **Yoruba**, and **Hausa**.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0+-00a393.svg)](https://fastapi.tiangolo.com)

---

## 🚀 Features

- 💬 **WhatsApp Integration** – Send & receive messages using WhatsApp Cloud API  
- 🔄 **Text & Voice Translation** – Supports both text and audio  
- ⚙️ **User Preferences** – Customizable language & output settings  
- 📝 **Web Forms** – Clean signup & settings pages  
- 🗄️ **Data Storage** – PostgreSQL with SQLAlchemy ORM  
- 🔒 **Message Deduplication** – Redis prevents repeat processing  
- 🎵 **Audio Processing** – WhatsApp-compatible audio conversion  
- 🗣️ **Spitch API** – Real-time translation & speech synthesis  

---

## 📁 Project Structure

```
wazobia/
├── app.py              # FastAPI app & endpoints
├── database.py         # SQLAlchemy models & session
├── models.py           # Translation logic
├── wa_handler.py       # WhatsApp webhook & media handling
├── templates/
│   ├── signup.html     # Signup page
│   └── settings.html   # Settings page
├── requirements.txt
└── README.md
```

---

## 🛠️ Setup & Installation

### ✅ Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- WhatsApp Business Account
- Spitch API credentials

### 🔧 Step 1: Clone & Create Virtual Environment

```bash
git clone <your-repo-url>
cd wazobia

# Create virtual environment
python -m venv wazobia

# Activate it
source wazobia/bin/activate  # macOS/Linux
# OR
wazobia\Scripts\activate     # Windows
```

### 📦 Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### ⚙️ Step 3: Configure Environment

Create a `.env` file with:

```env
DB_URL="postgresql://<user>:<pass>@<host>/<db>?sslmode=require"
WA_PHONE_NUMBER_ID="your-whatsapp-phone-id"
WA_VERIFY_TOKEN="your-verify-token"
WA_ACCESS_TOKEN="your-access-token"
SPITCH_API_KEY="your-spitch-api-key"
REDIS_HOST="redis-host"
REDIS_PORT="6379"
REDIS_USERNAME="redis-user"
REDIS_PASSWORD="redis-password"
SIGNUP="https://<your-domain>/signup"
SETTINGS="https://<your-domain>/settings"
```

---

## 🚀 Run the App

```bash
uvicorn app:app --reload
```

Visit:
- 📝 Signup → [http://localhost:8000/signup](http://localhost:8000/signup)  
- ⚙️ Settings → [http://localhost:8000/settings](http://localhost:8000/settings)

---

## 🔗 WhatsApp Integration

1. Use **ngrok** or **Azure Dev Tunnels** to expose your server  
2. Set WhatsApp webhook to `/webhook`  
3. Ensure the verify token matches your `.env`

---

## 📱 Usage Guide

### 👤 Signup
1. Visit the signup page  
2. Enter your WhatsApp number  
3. Choose language and output settings  

### ⚙️ Update Preferences
- Default language  
- Output language  
- Response format (text / voice / both)

### 🔄 Translation Flow
1. Send text/voice message to bot  
2. Get translated output as:
   - 📝 Text  
   - 🎤 Voice  
   - ✨ Both  

---

## 🌐 Supported Languages

| Language | Code |
|----------|------|
| English  | `en` |
| Igbo     | `ig` |
| Yoruba   | `yo` |
| Hausa    | `ha` |

---

## 📡 API Endpoints

| Method | Endpoint         | Description            |
|--------|------------------|------------------------|
| GET    | `/signup`        | Render signup form     |
| POST   | `/signup`        | Register new user      |
| GET    | `/settings`      | Render settings form   |
| POST   | `/settings`      | Update user preferences|
| GET    | `/webhook`       | Webhook verification   |
| POST   | `/webhook`       | WhatsApp message hook  |
| POST   | `/send_message`  | Test message sending   |

---

## 📝 Technical Notes

- Audio auto-converted to WhatsApp-compatible format  
- Redis blocks duplicate processing  
- Spitch API handles translation + TTS

---

## 📄 License

This project is under the **MIT License** – see [LICENSE](LICENSE).

---

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)  
- [SQLAlchemy](https://www.sqlalchemy.org/)  
- [Spitch API](https://spitch.io/)  
- [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)  
- [Redis](https://redis.io/)  
- [Jinja2](https://jinja.palletsprojects.com/)
