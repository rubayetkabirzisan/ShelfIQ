import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two GPS coordinates.
    Returns distance in metres.

    The Haversine formula accounts for Earth's curvature.
    For distances under ~10km (like outlet proximity checks),
    it's accurate to within a few centimetres.

    How it works:
    1. Convert degrees to radians
    2. Find the angular difference between the two points
    3. Apply the Haversine formula to get the central angle
    4. Multiply by Earth's radius to get the arc length (distance)
    """
    R = 6_371_000  # Earth's radius in metres

    # Convert decimal degrees to radians
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat   = math.radians(lat2 - lat1)
    dlon   = math.radians(lon2 - lon1)

    # Haversine formula
    a = (math.sin(dlat / 2) ** 2
         + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # distance in metres


def is_within_geofence(
    rep_lat: float, rep_lon: float,
    outlet_lat: float, outlet_lon: float,
    radius_metres: float = 100.0
) -> tuple[bool, float]:
    """
    Returns (is_within, distance_metres).
    Flagged as fraud if distance > radius_metres (default 100m).
    """
    distance = haversine_distance(rep_lat, rep_lon, outlet_lat, outlet_lon)
    return distance <= radius_metres, round(distance, 2)