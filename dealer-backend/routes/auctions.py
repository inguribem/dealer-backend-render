from fastapi import APIRouter, Query
import requests
import os

router = APIRouter(prefix="/auctions")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


@router.get("/nearby")
def get_auctions(city: str = Query(...)):

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": f"car auction in {city}",
        "key": GOOGLE_API_KEY
    }

    r = requests.get(url, params=params)

    if r.status_code != 200:
        return {"error": "Failed to fetch auctions"}

    results = r.json().get("results", [])

    auctions = []

    for place in results:
        auctions.append({
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating"),
            "location": place.get("geometry", {}).get("location")
        })

    return auctions