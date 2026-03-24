from fastapi import APIRouter, Form, BackgroundTasks
import requests
import os

router = APIRouter()

API_URL = os.getenv("API_URL")


def fetch_vehicle(vin: str, response_url: str):
    try:
        res = requests.get(f"{API_URL}/vehicle/{vin}")
        data = res.json()

        message = {
            "text": f"🚗 VIN: {vin}\nEstado: {data.get('status')}"
        }

        requests.post(response_url, json=message)

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