import requests
import json
BASE_URL = "http://localhost:8000"
login = requests.post(f"{BASE_URL}/api/auth/login/", json={
    "username": "rep",
    "password": "rep123"
})
token = login.json()["access"]
headers = {"Authorization": f"Bearer {token}"}
print("Login OK. Token acquired.")
IMAGE_PATH = r"E:\ShelfIQ\uploads\1f1a5bd4-8714-4dca-bbac-11e9eeb5a38c.jpg"
with open(IMAGE_PATH, "rb") as img:
    checkin = requests.post(
        f"{BASE_URL}/api/visits/checkin/",
        headers=headers,
        data={
            "outlet_id":    "1",
            "rep_name":     "AI Test Rep",
            "latitude":     "23.7806",
            "longitude":    "90.4193",
            "posm_ok":      "true",
            "checkin_time": "2026-05-29T14:00:00",
        },
        files={"image": ("shelf.jpg", img, "image/jpeg")}
    )
print("\n── Test 1: Check-in with image ──")
print(json.dumps(checkin.json(), indent=2))
visit_id = checkin.json().get("id")
print(f"\nVisit ID: {visit_id}")
print("\n── Test 2: AI Shelf Analysis ──")
analysis = requests.post(
    f"{BASE_URL}/api/analysis/analyze/",
    headers=headers,
    json={"visit_id": visit_id}
)
print(json.dumps(analysis.json(), indent=2))
print("\n── Test 3: Get Analysis by Visit ──")
get_analysis = requests.get(
    f"{BASE_URL}/api/analysis/visit/{visit_id}/",
    headers=headers
)
print(json.dumps(get_analysis.json(), indent=2))
print("\n── Test 4: Stats Dashboard ──")
stats = requests.get(
    f"{BASE_URL}/api/visits/stats/",
    headers=headers
)
print(json.dumps(stats.json(), indent=2))
print("\n── Test 5: Analyze visit with no image (should be 400) ──")
err = requests.post(
    f"{BASE_URL}/api/analysis/analyze/",
    headers=headers,
    json={"visit_id": 1}
)
print(f"Status: {err.status_code}")
print(json.dumps(err.json(), indent=2))
