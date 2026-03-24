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

        # 👇 DEBUG DIRECTO A SLACK
        requests.post(response_url, json={
            "text": f"DEBUG JSON:\n{data}"
        })

    except Exception as e:
        requests.post(response_url, json={
            "text": f"ERROR: {str(e)}"
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