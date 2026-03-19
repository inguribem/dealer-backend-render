import requests

def decode_vin(vin: str):

    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"

    r = requests.get(url)
    data = r.json()

    results = {
        item["Variable"]: item["Value"]
        for item in data["Results"]
        if item["Value"]
    }

    return {
        "vin": vin,
        "year": results.get("Model Year"),
        "make": results.get("Make"),
        "model": results.get("Model"),
        "trim": results.get("Trim"),
    }
