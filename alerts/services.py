from django.conf import settings
def _get_twilio_client():
    sid   = settings.TWILIO_ACCOUNT_SID
    token = settings.TWILIO_AUTH_TOKEN
    if not sid or not token:
        return None
    try:
        from twilio.rest import Client
        return Client(sid, token)
    except ImportError:
        return None
def _send_whatsapp(message: str) -> bool:
    client = _get_twilio_client()
    if not client:
        print("[WhatsApp] Twilio not configured - alert skipped.")
        return False
    try:
        client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=settings.TWILIO_WHATSAPP_TO,
            body=message
        )
        return True
    except Exception as e:
        print(f"[WhatsApp] Alert failed: {e}")
        return False
def send_checkin_alert(rep_name: str, outlet_name: str) -> bool:
    message = (
        f"ShelfIQ Check-in\n"
        f"Rep: {rep_name}\n"
        f"Outlet: {outlet_name}\n"
        f"Status: Visit recorded successfully."
    )
    return _send_whatsapp(message)
def send_fraud_alert(rep_name: str, outlet_name: str, fraud_types: list) -> bool:
    flags = ', '.join(fraud_types) if fraud_types else 'unknown'
    message = (
        f"ShelfIQ Fraud Alert\n"
        f"Rep: {rep_name}\n"
        f"Outlet: {outlet_name}\n"
        f"Flags: {flags}\n"
        f"Action required: Review visit immediately."
    )
    return _send_whatsapp(message)
def send_low_compliance_alert(outlet_name: str, score: float) -> bool:
    message = (
        f"ShelfIQ Low Compliance\n"
        f"Outlet: {outlet_name}\n"
        f"Compliance Score: {score:.1f}%\n"
        f"Action required: Arrange shelf restocking immediately."
    )
    return _send_whatsapp(message)
