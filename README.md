# ShelfIQ

ShelfIQ is a modular backend platform built to support retail operations, store analytics, fraud detection, alerts, and internal collaboration. It is designed as a professional, recruiter-friendly portfolio project that demonstrates strong backend engineering, API design, and business-critical data workflows.

## 🚀 Project Overview

ShelfIQ collects and manages retail data from users, outlets, and visits, and layers business insights, alerting, and fraud detection on top of that core dataset.

Key capabilities:
- User authentication and role-aware access control
- Outlet and store management
- Visit tracking and operational logging
- Alert generation for important events
- Fraud and suspicious activity detection
- Analysis-ready data services
- Lightweight internal chat/messaging endpoints

## 💡 Why this project stands out

ShelfIQ is built with a focus on real-world retail problems:
- Supports operational visibility across outlets and field visits
- Adds proactive protections through fraud detection rules
- Uses a clean Django REST architecture with JWT-based security
- Keeps the codebase modular so features can grow without becoming monolithic

## 📦 Architecture and Modules

The repository is organized into reusable Django apps:
- `accounts/` — custom user model, authentication endpoints, JWT integration
- `outlets/` — retail outlet metadata, inventory location data, store profiles
- `visits/` — visit records, activity logging, visit analytics
- `analysis/` — business insight utilities and analytic serializers
- `alerts/` — event notifications and alert creation workflows
- `fraud/` — suspicious behavior detection and risk scoring
- `chat/` — internal messaging / chat-style API endpoints

Additional developer utilities:
- `management/commands/seed_users.py` — seed the app with demo users
- `management/commands/seed_outlets.py` — seed the app with demo outlet data

## 🛠️ Technology Stack

- Python 3
- Django
- Django REST Framework (DRF)
- Simple JWT authentication
- django-cors-headers for frontend integration
- SQLite for lightweight development
- `.env`-driven configuration for secrets and API keys

## 🔧 Current Implementation Notes

The project is configured with a production-ready backend pattern:
- `AUTH_USER_MODEL = 'accounts.User'`
- JWT auth enforced globally via DRF settings
- CORS configured for modern frontend workflows
- Static and media handling configured for development
- Environment variables supported for secret management and Twilio/Gemini integration

## 🚀 Setup Instructions

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install django djangorestframework djangorestframework-simplejwt python-dotenv django-cors-headers
```

3. Apply migrations:

```powershell
python manage.py migrate
```

4. Create a superuser (optional):

```powershell
python manage.py createsuperuser
```

5. Run the development server:

```powershell
python manage.py runserver
```

## 🌐 Environment Variables

Use a `.env` file to provide secrets and third-party keys:
- `SECRET_KEY`
- `DEBUG`
- `GEMINI_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`
- `TWILIO_WHATSAPP_TO`

## 📂 How to Explore the Codebase

Start with these files and folders:
- `ShelfIQ/settings.py` — project configuration and installed apps
- `ShelfIQ/urls.py` — API routing and middleware setup
- `accounts/` — authentication and user model code
- `outlets/` and `visits/` — core retail data models
- `fraud/`, `alerts/`, `analysis/`, `chat/` — advanced business features

---

ShelfIQ is a strong backend demonstration project for recruiters seeking experience in commercial retail systems, API-driven architectures, and data-driven operational platforms.