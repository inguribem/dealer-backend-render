from fastapi import APIRouter, HTTPException
from database import get_connection
from models import Vehicle
from services.vin_service import decode_vin

router = APIRouter(prefix="/vehicles")

# -------------------------
# VIN LOOKUP (NHTSA)
# -------------------------
@router.get("/vin/{vin}")
def lookup_vin(vin: str):
    return decode_vin(vin)


# -------------------------
# GET INVENTORY
# -------------------------
@router.get("/inventory")
def get_inventory():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vehicles")

    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]

    result = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return result


# -------------------------
# ADD VEHICLE
# -------------------------
@router.post("/")
def add_vehicle(vehicle: Vehicle):

    if not vehicle.make or not vehicle.model:
        raise HTTPException(status_code=400, detail="make and model are required")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vehicles
        (vin, year, make, model, trim, price, miles, dealer_name, city, state)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (vin) DO NOTHING
    """, (
        vehicle.vin,
        vehicle.year,
        vehicle.make,
        vehicle.model,
        vehicle.trim,
        vehicle.price,
        vehicle.miles,
        vehicle.dealer_name,
        vehicle.city,
        vehicle.state
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "saved"}


# -------------------------
# UPDATE VEHICLE
# -------------------------
@router.put("/{vin}")
def update_vehicle(vin: str, vehicle: Vehicle):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE vehicles SET
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
        vehicle.year,
        vehicle.make,
        vehicle.model,
        vehicle.trim,
        vehicle.price,
        vehicle.miles,
        vehicle.dealer_name,
        vehicle.city,
        vehicle.state,
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

