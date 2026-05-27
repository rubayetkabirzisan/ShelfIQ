# ShelfIQ

ShelfIQ is a backend project for retail operations and store analytics. It is designed to collect and manage data about stores, visits, users, alerts, and suspicious activity so that businesses can make better decisions and stay secure.

## What this project does

- Stores user accounts and permissions for a retail app.
- Records outlet details and visit activity.
- Creates alerts and dashboards for important events.
- Includes a simple fraud-detection workflow to flag suspicious behavior.
- Supports a basic chat-style interface for internal communication.

## Why it matters

This project shows the ability to build a business-focused backend system that handles real retail needs, including:

- managing users and stores,
- tracking customer or visit interactions,
- detecting issues before they become larger problems,
- and keeping the system easy to extend.

## What is included

- `accounts/` — user and authentication logic.
- `outlets/` — store and outlet information.
- `visits/` — recording visits and activity.
- `analysis/` — business insight utilities.
- `alerts/` — notification and alert logic.
- `fraud/` — suspicious activity checks.
- `chat/` — lightweight messaging endpoints.

## Technology overview

- Built with Django, a popular Python web framework.
- Uses a local SQLite database for development.
- Organized into separate app modules so each part of the project is easy to understand and extend.

## Getting started

For developers who want to run the project locally:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
