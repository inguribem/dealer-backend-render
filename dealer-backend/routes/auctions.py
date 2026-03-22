from fastapi import APIRouter, Query
import requests
import os

router = APIRouter(prefix="/auctions")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# =========================
# GET AUCTIONS NEARBY
# =========================
@router.get("/nearby")
def get_auctions(city: str = Query(...)):

    # -------------------------
    # VALIDATE API KEY
    # -------------------------
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY not set")
        return []

    # -------------------------
    # GOOGLE PLACES REQUEST
    # -------------------------
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": f"car auction in {city}",
        "key": GOOGLE_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return []

    if response.status_code != 200:
        print(f"❌ Bad response: {response.status_code}")
        return []

    try:
        data = response.json()
    except:
        print("❌ Invalid JSON from Google API")
        return []

    results = data.get("results", [])

    # -------------------------
    # FORMAT RESPONSE
    # -------------------------
    auctions = []

    for place in results:

        location = place.get("geometry", {}).get("location", {})

        auctions.append({
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating"),
            "location": {
                "lat": location.get("lat"),
                "lng": location.get("lng")
            }
        })

    return auctions