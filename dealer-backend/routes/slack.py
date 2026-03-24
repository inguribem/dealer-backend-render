from fastapi import APIRouter, Form, BackgroundTasks
import requests
import os

router = APIRouter()

API_URL = os.getenv("API_URL")


def fetch_vehicle(vin: str, response_url: str):
    import requests

    try:
        print("➡️ Consultando API...")
        res = requests.get(f"{API_URL}/reports/vehicle", params={"vin": vin})
        print("STATUS:", res.status_code)
        
        data = res.json()

        print("➡️ Enviando respuesta a Slack...")

        r = requests.post(response_url, json={
            "text": f"🚗 VIN: {vin}\nEstado: {data.get('status')}"
        })

        print("SLACK STATUS:", r.status_code)
        print("SLACK RESPONSE:", r.text)

    except Exception as e:
        print("ERROR:", str(e))


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