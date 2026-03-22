# backend/routes/catalog.py
from fastapi import APIRouter
from database import get_connection  # tu función de conexión a la DB

router = APIRouter()

@router.get("/catalog-items")
def get_catalog_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type, base_price, sku FROM catalog_items")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    items = [
        {"id": r[0], "name": r[1], "type": r[2], "base_price": float(r[3]), "sku": r[4]}
        for r in rows
    ]
    return items
