import hashlib
import math
from datetime import datetime, time

from PIL import Image, ImageFilter
import numpy as np

# ─────────────────────────────────────────────────────────────
# Why is this in engine.py and not views.py?
#
# These are pure logic functions. They don't import Django models,
# don't touch the database, and don't handle HTTP requests.
# Keeping them here means:
# 1. They're easy to test in isolation
# 2. views.py stays clean — it just calls these functions
# 3. You can reuse them anywhere without pulling in HTTP logic
# ─────────────────────────────────────────────────────────────


# ── Check 1: Duplicate image detection ────────────────────────────────────────

def compute_md5(image_file) -> str:
    """
    Compute the MD5 hash of an uploaded image file.

    MD5 takes any input (a file's bytes) and produces a fixed-length
    32-character hex string. The same file always produces the same hash.
    Different files (even slightly) produce completely different hashes.

    This lets us detect if a rep uploads the exact same photo twice
    without storing or comparing the full image data.
    """
    md5 = hashlib.md5()

    # Read the file in 8KB chunks to handle large images
    # without loading the entire file into memory at once
    image_file.seek(0)  # Reset file pointer to the beginning
    for chunk in iter(lambda: image_file.read(8192), b''):
        md5.update(chunk)

    image_file.seek(0)  # Reset again so the file can be read later
    return md5.hexdigest()


def check_duplicate(image_file, visit_id: int) -> tuple[bool, str]:
    """
    Returns (is_duplicate, detail_message).

    Imports inside the function to avoid circular imports —
    engine.py is imported by views.py which imports models.
    Putting the import here means it only runs when this function
    is actually called.
    """
    from fraud.models import FraudLog
    from visits.models import Visit

    if image_file is None:
        return False, 'No image provided — duplicate check skipped.'

    current_hash = compute_md5(image_file)

    # Look through all previous visits that have images
    # and compare their MD5 hashes to the current one
    previous_visits = Visit.objects.filter(
        image__isnull=False
    ).exclude(id=visit_id)

    for prev_visit in previous_visits:
        if not prev_visit.image:
            continue
        try:
            with prev_visit.image.open('rb') as prev_file:
                prev_hash = compute_md5(prev_file)
            if prev_hash == current_hash:
                return True, (
                    f'Image is identical to visit #{prev_visit.id} '
                    f'({prev_visit.rep_name} at {prev_visit.outlet.name}). '
                    f'MD5: {current_hash}'
                )
        except (FileNotFoundError, OSError):
            # Previous image file was deleted from disk — skip it
            continue

    return False, f'Image is unique. MD5: {current_hash}'


# ── Check 2: Blur detection ────────────────────────────────────────────────────

BLUR_THRESHOLD = 8.0
# Images with a sharpness score below this are considered too blurry.
# Lower value = more lenient. Higher value = stricter.
# 8.0 is calibrated for typical shelf photos.

def check_blur(image_file) -> tuple[bool, str]:
    """
    Returns (is_blurry, detail_message).

    How blur detection works:
    1. Convert the image to grayscale (colour doesn't affect sharpness)
    2. Apply an edge-detection filter (FIND_EDGES)
       - Sharp images have strong, clear edges → high variance
       - Blurry images have weak, soft edges → low variance
    3. Compute the standard deviation of the edge pixel values
       - High std dev = lots of strong edges = sharp image
       - Low std dev  = few weak edges     = blurry image
    4. If std dev < BLUR_THRESHOLD → flagged as blurry

    This is classical signal processing, not ML.
    """
    if image_file is None:
        return False, 'No image provided — blur check skipped.'

    try:
        image_file.seek(0)
        img = Image.open(image_file)

        # Check minimum size — tiny images are always "blurry"
        width, height = img.size
        if width < 100 or height < 100:
            return True, (
                f'Image too small ({width}x{height}px). '
                f'Minimum required: 100x100px.'
            )

        # Convert to grayscale — L mode = luminance only
        gray = img.convert('L')

        # Apply edge detection filter
        edges = gray.filter(ImageFilter.FIND_EDGES)

        # Convert to numpy array for statistics
        edge_array = np.array(edges, dtype=np.float32)

        # Standard deviation measures how spread out the edge values are
        sharpness_score = float(np.std(edge_array))

        is_blurry = sharpness_score < BLUR_THRESHOLD

        status = 'BLURRY' if is_blurry else 'SHARP'
        return is_blurry, (
            f'Sharpness score: {sharpness_score:.2f} '
            f'(threshold: {BLUR_THRESHOLD}). '
            f'Result: {status}.'
        )

    except Exception as e:
        # If PIL can't open the file, treat it as not blurry
        # (don't penalise the rep for an unsupported format)
        return False, f'Blur check could not be completed: {str(e)}'


# ── Check 3: GPS geofence ──────────────────────────────────────────────────────

def check_gps(
    rep_lat: float, rep_lon: float,
    outlet_lat: float, outlet_lon: float,
    radius_metres: float = 100.0
) -> tuple[bool, str]:
    """
    Returns (is_flagged, detail_message).

    Reuses the Haversine logic from visits/utils.py.
    We import it here rather than duplicating the code.
    """
    from visits.utils import haversine_distance

    distance = haversine_distance(rep_lat, rep_lon, outlet_lat, outlet_lon)
    is_flagged = distance > radius_metres

    if is_flagged:
        return True, (
            f'Rep is {distance:.1f}m from outlet '
            f'(allowed: {radius_metres}m). GPS fraud suspected.'
        )
    return False, (
        f'Rep is {distance:.1f}m from outlet. Within geofence.'
    )


# ── Check 4: Timestamp validation ─────────────────────────────────────────────

BUSINESS_HOURS_START = time(8, 0)   # 08:00
BUSINESS_HOURS_END   = time(20, 0)  # 20:00

def check_timestamp(checkin_time: datetime) -> tuple[bool, str]:
    """
    Returns (is_flagged, detail_message).

    Flags the visit if:
    - The check-in time is in the future (more than 5 min buffer)
    - The check-in time is outside 08:00–20:00

    We use .replace(tzinfo=None) to strip timezone info before
    comparing, because checkin_time from the DB is timezone-aware
    and datetime.utcnow() is timezone-naive.
    Django stores times in UTC; we compare the time component only.
    """
    from django.utils import timezone

    now = timezone.now()

    # Strip timezone for comparison
    checkin_naive = checkin_time.replace(tzinfo=None) if checkin_time.tzinfo else checkin_time
    now_naive     = now.replace(tzinfo=None)

    # Check 1: Future timestamp (allow 5 minute buffer for clock drift)
    future_buffer_seconds = 300  # 5 minutes
    delta_seconds = (checkin_naive - now_naive).total_seconds()

    if delta_seconds > future_buffer_seconds:
        return True, (
            f'Check-in time {checkin_time} is {delta_seconds/60:.1f} minutes '
            f'in the future. Timestamp anomaly detected.'
        )

    # Check 2: Outside business hours (compare time component only)
    checkin_local_time = checkin_naive.time()

    if not (BUSINESS_HOURS_START <= checkin_local_time <= BUSINESS_HOURS_END):
        return True, (
            f'Check-in at {checkin_local_time.strftime("%H:%M")} is outside '
            f'business hours ({BUSINESS_HOURS_START.strftime("%H:%M")}–'
            f'{BUSINESS_HOURS_END.strftime("%H:%M")}).'
        )

    return False, (
        f'Check-in at {checkin_time} is within business hours and not in the future.'
    )


# ── Master function: run all 4 checks ─────────────────────────────────────────

def run_all_checks(visit, image_file=None) -> dict:
    """
    Runs all 4 fraud checks for a visit and returns a results dict.

    This is the single entry point that views.py calls.
    It collects all results and computes the overall is_fraud verdict.

    Args:
        visit:      The Visit model instance
        image_file: The uploaded image file object (or None)

    Returns:
        dict with all check results, ready to create a FraudLog
    """
    # Run each check
    dup_flag,  dup_detail  = check_duplicate(image_file, visit.id)
    blur_flag, blur_detail = check_blur(image_file)
    gps_flag,  gps_detail  = check_gps(
        rep_lat=visit.latitude,
        rep_lon=visit.longitude,
        outlet_lat=visit.outlet.latitude,
        outlet_lon=visit.outlet.longitude,
    )
    ts_flag,   ts_detail   = check_timestamp(visit.checkin_time)

    # Overall verdict
    is_fraud = any([dup_flag, blur_flag, gps_flag, ts_flag])

    return {
        'is_duplicate':     dup_flag,
        'is_blurry':        blur_flag,
        'is_gps_flagged':   gps_flag,
        'is_timestamp_bad': ts_flag,
        'is_fraud':         is_fraud,
        'duplicate_detail': dup_detail,
        'blur_detail':      blur_detail,
        'gps_detail':       gps_detail,
        'timestamp_detail': ts_detail,
    }