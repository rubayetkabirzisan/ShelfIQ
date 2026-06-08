# ShelfIQ

ShelfIQ is a Django backend for retail field operations and store check-ins. It provides a secure API for user authentication, outlet discovery, visit logging, and fraud detection with a modular app structure.

## 🚀 What ShelfIQ Does

ShelfIQ is built to support retail sales reps and supervisors by:
- Authenticating users with JWT tokens
- Serving active outlet data for check-in workflows
- Recording visit check-ins with GPS, notes, and optional shelf images
- Validating location accuracy with a geofence check
- Running fraud checks on visits and storing audit-ready results
- Exposing supervisor-only fraud log dashboards

## 📦 Active Apps

- `accounts/` — custom `User` model with rep/supervisor roles, login, and current-user endpoints
- `outlets/` — active retail outlet catalog and location metadata
- `visits/` — check-in workflow, visit list/detail views, GPS validation, image upload support
- `fraud/` — fraud check runner, fraud log persistence, and supervisor audit endpoints

## 🔌 API Endpoints

Authentication
- `POST /api/auth/login/` — username/password → JWT access + refresh tokens
- `GET /api/auth/me/` — current authenticated user details

Outlets
- `GET /api/visits/outlets/` — list active outlets for reps before login/check-in

Visits
- `POST /api/visits/checkin/` — submit a visit, optional image, and geofence validation
- `GET /api/visits/` — list visits with optional `outlet_id` or `rep_name` filters
- `GET /api/visits/<id>/` — visit detail by ID

Fraud
- `POST /api/fraud/check/` — run fraud checks for a visit and save the result
- `GET /api/fraud/logs/` — supervisor-only fraud log listing
- `GET /api/fraud/visit/<visit_id>/` — fraud log lookup by visit ID

## 🛠️ Technology Stack

- Python 3
- Django
- Django REST Framework
- djangorestframework-simplejwt
- django-cors-headers
- SQLite for development
- Pillow for image uploads
- `.env` configuration for secrets and API keys

## 🧩 Key Design Points

- `AUTH_USER_MODEL = 'accounts.User'` with role support for reps and supervisors
- JWT auth enforced globally via DRF settings
- CORS allowed for `http://localhost:3000`
- Media uploads served from `media/` in development
- Geofence validation flags visits that occur outside the outlet location
- Fraud engine persists detailed flags and descriptions for each visit

## 🚀 Local Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install django djangorestframework djangorestframework-simplejwt python-dotenv django-cors-headers pillow
```

3. Apply migrations:

```powershell
python manage.py migrate
```

4. Seed demo data:

```powershell
python manage.py seed_users
python manage.py seed_outlets
```

5. Run the development server:

```powershell
python manage.py runserver
```

## 📁 Environment Configuration

Create a `.env` file for local development values:
- `SECRET_KEY`
- `DEBUG` (set to `True` or `False`)
- `GEMINI_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`
- `TWILIO_WHATSAPP_TO`

## 🚧 Notes

- The current app wiring uses `accounts`, `outlets`, `visits`, and `fraud`.
- Uploaded visit images are stored under `media/shelf_images/` and served in development when `DEBUG=True`.
- The `seed_users` and `seed_outlets` commands provide initial demo content for local testing.

## 🔎 Useful Files

- `ShelfIQ/settings.py` — project configuration and installed apps
- `ShelfIQ/urls.py` — API routing and static/media setup
- `accounts/` — auth, custom user model, serializers, views
- `outlets/` — outlet model, serializer, public outlet list
- `visits/` — visit check-in logic, serializers, views
- `fraud/` — fraud engine wrapper, serializers, and audit endpoints

ShelfIQ is a focused backend demo for retail operations and fraud-aware visit tracking.