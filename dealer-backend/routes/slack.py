from fastapi import APIRouter, Form, BackgroundTasks
import requests
import os

router = APIRouter()

API_URL = os.getenv("API_URL")


def fetch_vehicle(vin: str, response_url: str):
    import requests

    try:
        res = requests.get(
            f"{API_URL}/reports/vehicle",
            params={"vin": vin},
            timeout=10
        )

        data = res.json()

        vehicle = data.get("vehicle", {})
        summary = data.get("summary", {})

        estado = vehicle.get("status", "No disponible")
        precio = vehicle.get("price_purchase", "N/A")
        total_orders = summary.get("total_orders", 0)
        total_spent = summary.get("total_spent", 0)

        requests.post(response_url, json={
            "response_type": "in_channel",
            "text": f"""
🚗 *Reporte de Vehículo*
VIN: {vin}
Estado: {estado}
💰 Compra: ${precio}

📦 Órdenes: {total_orders}
💸 Total invertido: ${total_spent}
"""
        })

    except Exception as e:
        requests.post(response_url, json={
            "text": f"Error: {str(e)}"
        })


@router.post("/slack/vehicle")
async def slack_vehiculo(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    response_url: str = Form(...)
):
    vin = text.strip()

    # 👉 responder inmediato
    background_tasks.add_task(fetch_vehicle, vin, response_url)

    return {
        "response_type": "ephemeral",
        "text": "🔍 Buscando vehículo..."
    }
    
@router.get("/slack/oauth/callback")
def slack_oauth_callback():
    return {"status": "ok"}