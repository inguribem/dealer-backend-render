from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

router = APIRouter()

DB_URL = os.getenv("DATABASE_URL")  # Tu conexión a PostgreSQL

def get_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

# -------------------------
# CREATE SERVICE ORDER
# -------------------------
@router.post("/service-orders")
def create_service_order(vehicle_id: int = Query(..., description="ID of the vehicle")):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO service_orders (vehicle_id, status, total_cost, created_at)
            VALUES (%s, 'pending', 0, NOW())
            RETURNING id
            """,
            (vehicle_id,)
        )
        order_id = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
        return JSONResponse({"order_id": order_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating service order: {e}")


# -------------------------
# GET SERVICE ORDERS
# -------------------------
@router.get("/service-orders")
def get_service_orders(vehicle_id: Optional[int] = Query(None)):
    try:
        conn = get_connection()
        cur = conn.cursor()
        if vehicle_id:
            cur.execute(
                "SELECT id, vehicle_id, status, total_cost, created_at FROM service_orders WHERE vehicle_id=%s ORDER BY created_at DESC",
                (vehicle_id,)
            )
        else:
            cur.execute(
                "SELECT id, vehicle_id, status, total_cost, created_at FROM service_orders ORDER BY created_at DESC"
            )
        orders = cur.fetchall()
        cur.close()
        conn.close()
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching service orders: {e}")


# -------------------------
# ADD ITEM TO ORDER
# -------------------------
@router.post("/order-details")
def add_order_detail(
    order_id: int,
    catalog_item_id: int,
    quantity: int = 1,
    unit_price: float = 0
):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verifica que la orden exista
        cur.execute("SELECT id FROM service_orders WHERE id=%s", (order_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        # Inserta el item
        cur.execute(
            """
            INSERT INTO order_details (order_id, catalog_item_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (order_id, catalog_item_id, quantity, unit_price)
        )
        detail_id = cur.fetchone()["id"]

        # Actualiza el total de la orden
        cur.execute(
            "UPDATE service_orders SET total_cost = total_cost + %s WHERE id=%s",
            (quantity * unit_price, order_id)
        )

        conn.commit()
        cur.close()
        conn.close()
        return JSONResponse({"order_detail_id": detail_id})
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding order detail: {e}")


# -------------------------
# GET ORDER DETAILS
# -------------------------
@router.get("/order-details")
def get_order_details(order_id: int = Query(..., description="ID of the service order")):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT od.id, od.order_id, od.catalog_item_id, od.quantity, od.unit_price,
                   ci.name as item_name, ci.type as item_type
            FROM order_details od
            LEFT JOIN catalog_items ci ON od.catalog_item_id = ci.id
            WHERE od.order_id=%s
            """,
            (order_id,)
        )
        details = cur.fetchall()
        cur.close()
        conn.close()
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order details: {e}")



