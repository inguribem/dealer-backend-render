from fastapi import APIRouter, Query
from typing import Optional
from database import get_connection
import requests
import os

router = APIRouter(prefix="/vehicles")

# -------------------------
# VIN Lookup via NHTSA
# -------------------------
@router.get("/vin/{vin}")
def lookup_vin(vin: str):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    r = requests.get(url)
    data = r.json()
    resultados = {item['Variable']: item['Value'] for item in data['Results'] if item['Value']}
    campos = ["Make","Model","Model Year","Vehicle Type","Engine Cylinders",
              "Fuel Type - Primary","Transmission Style","Body Class"]
    resumen = {c: resultados.get(c,"N/A") for c in campos}
    return resumen

# -------------------------
# ADD VEHICLE
# -------------------------
@router.post("/")
def add_vehicle(vehicle: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vehicles
        (vin, year, make, model, trim, price_purchase, miles, dealer_name, city, state, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (vin) DO NOTHING
    """, (
        vehicle["vin"],
        vehicle.get("year") or None,
        vehicle.get("make") or None,
        vehicle.get("model") or None,
        vehicle.get("trim") or "",
        vehicle.get("price_purchase") or None,
        vehicle.get("miles") or None,
        vehicle.get("dealer_name") or "",
        vehicle.get("city") or "",
        vehicle.get("state") or ""
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "saved"}

# -------------------------
# VEHICLE INVENTORY WITH FILTERS
# -------------------------
@router.get("/inventory")
def get_inventory(
    search: Optional[str] = Query(None),
    make: Optional[str] = Query(None),
    year: Optional[int] = Query(None)
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT vin, year, make, model, price_purchase, miles,
               trim, dealer_name, city, state, status
        FROM vehicles
        WHERE 1=1
    """

    params = []

    if search:
        query += " AND (vin ILIKE %s OR model ILIKE %s OR make ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    if make:
        query += " AND make ILIKE %s"
        params.append(f"%{make}%")

    if year:
        query += " AND year = %s"
        params.append(year)

    query += " ORDER BY year DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    conn.close()

    return [dict(zip(columns, row)) for row in rows]

# -------------------------
# UPDATE VEHICLE
# -------------------------
@router.put("/{vin}")
def update_vehicle(vin: str, vehicle: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE vehicles
        SET year=%s, make=%s, model=%s, trim=%s,
            price_purchase=%s, miles=%s,
            dealer_name=%s, city=%s, state=%s, status=%s
        WHERE vin=%s
    """, (
        vehicle.get("year"),
        vehicle.get("make"),
        vehicle.get("model"),
        vehicle.get("trim", ""),
        vehicle.get("price_purchase"),
        vehicle.get("miles"),
        vehicle.get("dealer_name", ""),
        vehicle.get("city", ""),
        vehicle.get("state", ""),
        vehicle.get("status", "new"),
        vin
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "updated"}

# -------------------------
# DELETE VEHICLE
# -------------------------
@router.delete("/{vin}")
def delete_vehicle(vin: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE vin=%s", (vin,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "deleted"}


