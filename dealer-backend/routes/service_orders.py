from fastapi import APIRouter, Query
from typing import Optional
from database import get_connection
import requests
import os

router = APIRouter(prefix="/service=orders")

# -------------------------
# CREATE SERVICE ORDER
# -------------------------
@router.post("/service-orders")
def create_order(vehicle_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO service_orders (vehicle_id, status)
        VALUES (%s, 'in_progress')
        RETURNING id
    """, (vehicle_id,))

    order_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return {"order_id": order_id}


# -------------------------
# ADD ITEM TO SERVICE ORDER
# -------------------------
@router.post("/service-orders/{order_id}/items")
def add_item(order_id: int, catalog_item_id: int, quantity: int = 1):

    conn = get_connection()
    cur = conn.cursor()

    # obtener precio base
    cur.execute("SELECT base_price FROM catalog_items WHERE id=%s", (catalog_item_id,))
    price = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO order_details (order_id, catalog_item_id, quantity, unit_price)
        VALUES (%s,%s,%s,%s)
    """, (order_id, catalog_item_id, quantity, price))

    # actualizar total
    cur.execute("""
        UPDATE service_orders
        SET total_cost = (
            SELECT SUM(quantity * unit_price)
            FROM order_details
            WHERE order_id = %s
        )
        WHERE id = %s
    """, (order_id, order_id))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Item added"}

# -------------------------
# GET SERVICE ORDER WITH ITEMS
# -------------------------
@router.get("/service-orders/{order_id}")
def get_order(order_id: int):

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT so.*, v.vin, v.make, v.model
        FROM service_orders so
        JOIN vehicles v ON so.vehicle_id = v.id
        WHERE so.id = %s
    """, (order_id,))
    order = cur.fetchone()

    cur.execute("""
        SELECT od.*, ci.name, ci.type
        FROM order_details od
        JOIN catalog_items ci ON od.catalog_item_id = ci.id
        WHERE od.order_id = %s
    """, (order_id,))
    items = cur.fetchall()

    conn.close()

    return {
        "order": order,
        "items": items
    }


# -------------------------
# COMPLETE SERVICE ORDER
# -------------------------
@router.put("/service-orders/{order_id}/complete")
def complete_order(order_id: int):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE service_orders
        SET status='completed'
        WHERE id=%s
    """, (order_id,))

    conn.commit()
    conn.close()

    return {"message": "Order completed"}

