from google import genai
from google.genai import types
from django.conf import settings
def _get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)
def _build_db_context() -> str:
    from visits.models import Visit
    from fraud.models import FraudLog
    from analysis.models import ShelfAnalysis
    from django.db.models import Avg, Count
    total_visits   = Visit.objects.count()
    total_fraud    = FraudLog.objects.filter(is_fraud=True).count()
    avg_compliance = ShelfAnalysis.objects.aggregate(
        avg=Avg('compliance_score')
    )['avg'] or 0
    outlet_performance = ShelfAnalysis.objects.values(
        'visit__outlet__name'
    ).annotate(
        avg_score=Avg('compliance_score'),
        visit_count=Count('id')
    ).order_by('avg_score')[:3]
    recent_fraud = FraudLog.objects.filter(
        is_fraud=True
    ).select_related('visit', 'visit__outlet').order_by('-created_at')[:5]
    context = f"""
=== ShelfIQ Live Database Context ===
SUMMARY STATISTICS:
- Total store visits recorded: {total_visits}
- Total fraud cases detected: {total_fraud}
- Average shelf compliance score: {avg_compliance:.1f}%
WORST PERFORMING OUTLETS (lowest compliance):
"""
    for outlet in outlet_performance:
        context += (
            f"- {outlet['visit__outlet__name']}: "
            f"{outlet['avg_score']:.1f}% avg compliance "
            f"({outlet['visit_count']} visits)\n"
        )
    context += "\nRECENT FRAUD CASES:\n"
    for log in recent_fraud:
        flags = []
        if log.is_duplicate:     flags.append('duplicate image')
        if log.is_blurry:        flags.append('blurry image')
        if log.is_gps_flagged:   flags.append('GPS spoofing')
        if log.is_timestamp_bad: flags.append('timestamp anomaly')
        context += (
            f"- Visit #{log.visit_id} by {log.visit.rep_name} "
            f"at {log.visit.outlet.name}: {', '.join(flags)}\n"
        )
    context += "\n=== End of Database Context ==="
    return context
def get_retailgpt_response(user_message: str, username: str) -> str:
    try:
        client  = _get_client()
        context = _build_db_context()
        system_prompt = f"""You are RetailGPT, an intelligent retail operations
assistant for ShelfIQ. You help supervisors monitor shelf compliance,
detect sales rep fraud, and improve store performance.
You have access to live data from the ShelfIQ database:
{context}
Answer questions based on this data. Be concise, professional, and
actionable. If asked about something not in the data, say so clearly.
Always refer to specific outlet names and numbers when available."""
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[
                types.Part.from_text(text=system_prompt),
                types.Part.from_text(
                    text=f"Supervisor {username} asks: {user_message}"
                ),
            ]
        )
        return response.text
    except Exception as e:
        return (
            f"RetailGPT is temporarily unavailable: {str(e)}. "
            f"Please try again shortly."
        )
