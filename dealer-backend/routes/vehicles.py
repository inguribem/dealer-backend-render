from fastapi import APIRouter, HTTPException, Query
from database import get_connection
import requests
import os

router = APIRouter(prefix="/vehicles")

@router.get("/vin/{vin}")
def lookup_vin(vin: str):
    """Decodifica VIN usando NHTSA y busca MarketCheck si es posible"""
    # NHTSA
    nhtsa_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    try:
        r = requests.get(nhtsa_url, timeout=10)
        r.raise_for_status()
        results = r.json().get("Results", [])
        decoded = {item["Variable"]: item["Value"] for item in results if item["Value"]}
    except Exception:
        decoded = {}

    if not decoded:
        raise HTTPException(status_code=404, detail="VIN not found in NHTSA")

    # Preparar datos iniciales
    vehicle_data = {
        "vin": vin,
        "year": decoded.get("Model Year"),
        "make": decoded.get("Make"),
        "model": decoded.get("Model"),
        "trim": decoded.get("Trim", ""),
        "vehicle_type": decoded.get("Vehicle Type", ""),
        "engine_cylinders": decoded.get("Engine Cylinders", ""),
        "fuel_type": decoded.get("Fuel Type - Primary", ""),
        "transmission": decoded.get("Transmission Style", ""),
        "body_class": decoded.get("Body Class", "")
    }

    return vehicle_data


@router.post("/")
def add_vehicle(vehicle: dict):
    """Guarda vehículo en PostgreSQL con conversión segura de tipos"""
    required_fields = ["vin", "make", "model"]
    for f in required_fields:
        if not vehicle.get(f):
            raise HTTPException(status_code=400, detail=f"{f} is required")

    # Convertir tipos
    try:
        vehicle["year"] = int(vehicle.get("year")) if vehicle.get("year") else None
    except ValueError:
        vehicle["year"] = None

    try:
        vehicle["price"] = float(vehicle.get("price")) if vehicle.get("price") else None
    except ValueError:
        vehicle["price"] = None

    try:
        vehicle["miles"] = int(vehicle.get("miles")) if vehicle.get("miles") else None
    except ValueError:
        vehicle["miles"] = None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vehicles
        (vin, year, make, model, trim, price, miles, dealer_name, city, state)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (vin) DO NOTHING
    """, (
        vehicle["vin"],
        vehicle["year"],
        vehicle.get("make"),
        vehicle.get("model"),
        vehicle.get("trim"),
        vehicle.get("price"),
        vehicle.get("miles"),
        vehicle.get("dealer_name"),
        vehicle.get("city"),
        vehicle.get("state")
    ))
    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "saved"}

@router.get("/inventory")
def get_inventory(
    vin: str = None,
    make: str = None,
    model: str = None,
    year_min: int = None,
    year_max: int = None,
    price_min: float = None,
    price_max: float = None
):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT vin, year, make, model, trim, price, miles, dealer_name, city, state
    FROM vehicles
    WHERE TRUE
    """

    params = []

    if vin:
        query += " AND vin = %s"
        params.append(vin)

    if make:
        query += " AND make ILIKE %s"
        params.append(f"%{make}%")

    if model:
        query += " AND model ILIKE %s"
        params.append(f"%{model}%")

    if year_min:
        query += " AND (year >= %s OR year IS NULL)"
        params.append(year_min)

    if year_max:
        query += " AND (year <= %s OR year IS NULL)"
        params.append(year_max)

    if price_min:
        query += " AND (price >= %s OR price IS NULL)"
        params.append(price_min)

    if price_max:
        query += " AND (price <= %s OR price IS NULL)"
        params.append(price_max)

    query += " ORDER BY year DESC"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    columns = ["vin","year","make","model","trim","price","miles","dealer_name","city","state"]

    return [dict(zip(columns,row)) for row in rows]

@router.put("/{vin}")
def update_vehicle(vin: str, vehicle: dict):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE vehicles
        SET
            year=%s,
            make=%s,
            model=%s,
            trim=%s,
            price=%s,
            miles=%s,
            dealer_name=%s,
            city=%s,
            state=%s
        WHERE vin=%s
    """, (
        vehicle.get("year"),
        vehicle.get("make"),
        vehicle.get("model"),
        vehicle.get("trim"),
        vehicle.get("price"),
        vehicle.get("miles"),
        vehicle.get("dealer_name"),
        vehicle.get("city"),
        vehicle.get("state"),
        vin
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "updated"}

@router.delete("/{vin}")
def delete_vehicle(vin: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM vehicles WHERE vin=%s", (vin,))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "deleted"}
