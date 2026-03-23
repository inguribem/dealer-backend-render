from fastapi import APIRouter
from pydantic import BaseModel
from database import get_connection

router = APIRouter()

# -------------------------
# MODELOS Pydantic
# -------------------------
class OrderDetailCreate(BaseModel):
    order_id: int
    catalog_item_id: int
    quantity: int
    unit_price: float

class ServiceOrderCreate(BaseModel):
    vehicle_id: int

# -------------------------
# ENDPOINTS
# -------------------------
@router.post("/service-orders")
def create_service_order(order: ServiceOrderCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO service_orders (vehicle_id, status, total_cost) VALUES (%s, %s, %s) RETURNING id",
        (order.vehicle_id, "in_progress", 0)
    )
    order_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {"order_id": order_id}


@router.get("/service-orders")
def get_vehicle_orders(vehicle_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, status, total_cost, created_at FROM service_orders WHERE vehicle_id = %s ORDER BY created_at DESC",
        (vehicle_id,)
    )
    orders = cursor.fetchall()
    conn.close()
    if orders:
        return [
            {"id": o[0], "status": o[1], "total_cost": float(o[2]), "created_at": o[3].isoformat()}
            for o in orders
        ]
    return []


@router.get("/catalog-items")
def get_catalog_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type, base_price FROM catalog_items")
    items = cursor.fetchall()
    conn.close()
    return [
        {"id": i[0], "name": i[1], "type": i[2], "base_price": float(i[3])}
        for i in items
    ]


@router.post("/order-details")
def add_order_detail(item: OrderDetailCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO order_details (order_id, catalog_item_id, quantity, unit_price)
        VALUES (%s, %s, %s, %s)
        """,
        (item.order_id, item.catalog_item_id, item.quantity, item.unit_price)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}

@router.get("/order-details")
def get_order_details(order_id: int):
    """
    Devuelve todos los items asociados a una orden específica.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, order_id, catalog_item_id, quantity, unit_price
            FROM order_details
            WHERE order_id = %s
            """,
            (order_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return []

        # Convertimos a lista de diccionarios
        result = [
            {
                "id": row[0],
                "order_id": row[1],
                "catalog_item_id": row[2],
                "quantity": row[3],
                "unit_price": float(row[4]),  # evita problemas JSON
            }
            for row in rows
        ]
        return result

    except Exception as e:
        cursor.close()
        conn.close()
        return {"error": str(e)}

@router.put("/service-orders/{order_id}")
def update_service_order(order_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE service_orders SET status = %s WHERE id = %s",
        (status, order_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}

@router.delete("/service-orders/{order_id}")
def delete_service_order(order_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    # Opcional: eliminar también order_details relacionados
    cursor.execute("DELETE FROM order_details WHERE order_id = %s", (order_id,))
    cursor.execute("DELETE FROM service_orders WHERE id = %s", (order_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}

@router.put("/order-details/{detail_id}")
def update_order_detail(detail_id: int, quantity: int, unit_price: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE order_details SET quantity = %s, unit_price = %s WHERE id = %s",
        (quantity, unit_price, detail_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}

@router.delete("/order-details/{detail_id}")
def delete_order_detail(detail_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM order_details WHERE id = %s", (detail_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}

