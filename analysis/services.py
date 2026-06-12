import base64
import json
import re

from google import genai
from google.genai import types
from django.conf import settings


def _get_gemini_client():
    """
    Configure and return the Gemini client using the new google-genai SDK.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set in your .env file. "
            "Get one at https://aistudio.google.com/app/apikey"
        )
    return genai.Client(api_key=api_key)


def _encode_image_to_base64(image_file) -> tuple[str, str]:
    """
    Convert an image file to Base64 and detect its MIME type.
    Returns (base64_string, mime_type).
    """
    image_file.seek(0)
    image_bytes = image_file.read()
    image_file.seek(0)

    file_name = getattr(image_file, 'name', 'image.jpg').lower()
    if file_name.endswith('.png'):
        mime_type = 'image/png'
    elif file_name.endswith('.webp'):
        mime_type = 'image/webp'
    else:
        mime_type = 'image/jpeg'

    return base64.b64encode(image_bytes).decode('utf-8'), mime_type


def _build_prompt() -> str:
    return """You are a retail shelf compliance analyst for ShelfIQ.

Analyse this shelf image and count the visible product facings.

TARGET BRAND: Foodie Noodles Olympics (look for 'Foodie', 'Olympics' branding)
COMPETITOR:   Mr. Noodles and any other noodle brand

Count every visible product facing (front-facing product unit on shelf).

Respond with ONLY a valid JSON object in this exact format — no markdown,
no explanation, just the JSON:

{
  "our_count": <integer>,
  "competitor_count": <integer>,
  "compliance_score": <float 0-100>,
  "supervisor_summary": "<2-3 sentence summary of shelf status and recommendations>",
  "confidence": "<high|medium|low>"
}

Calculate compliance_score as: (our_count / (our_count + competitor_count)) * 100
If no products are visible or you cannot analyse the image, return all zeros
and explain in supervisor_summary."""


def _parse_gemini_response(response_text: str) -> dict:
    """
    Parse Gemini's text response into a Python dict.
    Strips markdown code fences if present.
    """
    cleaned = re.sub(r'```(?:json)?\s*', '', response_text).strip()
    cleaned = cleaned.replace('```', '').strip()

    try:
        data = json.loads(cleaned)

        our_count        = max(0, int(data.get('our_count', 0)))
        competitor_count = max(0, int(data.get('competitor_count', 0)))
        total            = our_count + competitor_count

        compliance_score = round((our_count / total) * 100, 2) if total > 0 else 0.0

        return {
            'our_count':           our_count,
            'competitor_count':    competitor_count,
            'compliance_score':    compliance_score,
            'supervisor_summary':  str(data.get('supervisor_summary', '')),
            'raw_response':        response_text,
            'analysis_successful': True,
        }

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        return {
            'our_count':           0,
            'competitor_count':    0,
            'compliance_score':    0.0,
            'supervisor_summary':  f'Analysis could not be completed: {str(e)}',
            'raw_response':        response_text,
            'analysis_successful': False,
        }


def analyze_shelf_image(image_file, outlet_name: str = '') -> dict:
    """
    Main entry point — sends image to Gemini and returns analysis results.
    """
    try:
        client          = _get_gemini_client()
        image_b64, mime = _encode_image_to_base64(image_file)
        prompt          = _build_prompt()

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[
                types.Part.from_text(text=prompt),
                types.Part.from_bytes(
                    data=base64.b64decode(image_b64),
                    mime_type=mime,
                ),
            ]
        )

        return _parse_gemini_response(response.text)

    except ValueError as e:
        return {
            'our_count':           0,
            'competitor_count':    0,
            'compliance_score':    0.0,
            'supervisor_summary':  str(e),
            'raw_response':        '',
            'analysis_successful': False,
        }
    except Exception as e:
        return {
            'our_count':           0,
            'competitor_count':    0,
            'compliance_score':    0.0,
            'supervisor_summary':  f'Gemini API error: {str(e)}',
            'raw_response':        str(e),
            'analysis_successful': False,
        }