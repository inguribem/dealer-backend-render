from fastapi import APIRouter, Query
from database import get_connection

router = APIRouter(prefix="/reports")

# =========================
# VEHICLE REPORT
# =========================
@router.get("/vehicle")
def vehicle_report(vin: str = Query(...)):
    
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # -------------------------
        # GET VEHICLE INFO
        # -------------------------
        cursor.execute("""
            SELECT id, vin, year, make, model, price_purchase, status
            FROM vehicles
            WHERE vin = %s
        """, (vin,))
        
        vehicle = cursor.fetchone()

        if not vehicle:
            return {"error": "Vehicle not found"}

        vehicle_id = vehicle[0]

        vehicle_data = {
            "id": vehicle[0],
            "vin": vehicle[1],
            "year": vehicle[2],
            "make": vehicle[3],
            "model": vehicle[4],
            "price_purchase": float(vehicle[5]) if vehicle[5] else 0,
            "status": vehicle[6]
        }

        # -------------------------
        # GET SERVICE ORDERS
        # -------------------------
        cursor.execute("""
            SELECT id, status, total_cost, created_at
            FROM service_orders
            WHERE vehicle_id = %s
            ORDER BY created_at DESC
        """, (vehicle_id,))

        orders_rows = cursor.fetchall()

        orders = []

        for order in orders_rows:
            order_id = order[0]

            # -------------------------
            # GET ORDER DETAILS
            # -------------------------
            cursor.execute("""
                SELECT od.id, od.catalog_item_id, od.quantity, od.unit_price,
                       ci.name, ci.type
                FROM order_details od
                LEFT JOIN catalog_items ci
                    ON ci.id = od.catalog_item_id
                WHERE od.order_id = %s
            """, (order_id,))

            details_rows = cursor.fetchall()

            details = []
            total_order_cost = 0

            for d in details_rows:
                subtotal = float(d[2]) * float(d[3])
                total_order_cost += subtotal

                details.append({
                    "id": d[0],
                    "catalog_item_id": d[1],
                    "name": d[4],
                    "type": d[5],
                    "quantity": d[2],
                    "unit_price": float(d[3]),
                    "subtotal": subtotal
                })

            orders.append({
                "id": order_id,
                "status": order[1],
                "total_cost": float(order[2]) if order[2] else total_order_cost,
                "created_at": order[3].isoformat(),
                "details": details
            })

        # -------------------------
        # TOTALS SUMMARY
        # -------------------------
        total_spent = sum(o["total_cost"] for o in orders)

        report = {
            "vehicle": vehicle_data,
            "orders": orders,
            "summary": {
                "total_orders": len(orders),
                "total_spent": total_spent
            }
        }

        return report

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()