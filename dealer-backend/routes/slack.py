from fastapi import APIRouter, Form, BackgroundTasks
import requests
import os

router = APIRouter()

API_URL = os.getenv("API_URL")

# --- Funciones de Lógica (Tareas de fondo) ---

def fetch_vehicle(vin: str, response_url: str):
    try:
        res = requests.get(f"{API_URL}/reports/vehicle", params={"vin": vin}, timeout=10)
        data = res.json()
        vehicle = data.get("vehicle", {})
        summary = data.get("summary", {})

        requests.post(response_url, json={
            "response_type": "in_channel",
            "text": f"🚗 *Reporte de Vehículo*\nVIN: {vin}\nEstado: {vehicle.get('status', 'N/A')}\n💰 Compra: ${vehicle.get('price_purchase', 'N/A')}"
        })
    except Exception as e:
        requests.post(response_url, json={"text": f"Error: {str(e)}"})

def fetch_vehicles_by_year(year: str, response_url: str):
    """Toda la lógica de red ocurre aquí, fuera del ciclo de respuesta de Slack"""
    try:
        # 1. Consulta a la API externa
        res = requests.get(f"{API_URL}/vehicles/inventory", params={"year": year}, timeout=10)
        res.raise_for_status()
        vehicles = res.json()

        if not vehicles:
            text_result = f"No encontré vehículos del año *{year}*."
        else:
            count = len(vehicles)
            list_text = "\n".join([f"• {v.get('make')} {v.get('model')} (VIN: {v.get('vin')}) (Status: {v.get('status')})" for v in vehicles[:5]])
            text_result = f"📅 *Vehículos {year}* ({count} total):\n{list_text}"

        # 2. Enviamos la respuesta real a Slack mediante el response_url
        requests.post(response_url, json={
            "response_type": "in_channel",
            "text": text_result
        })

    except Exception as e:
        requests.post(response_url, json={"text": f"⚠️ Error en la búsqueda: {str(e)}"})

# --- Endpoints ---

@router.post("/slack/vehicle")
async def slack_vehiculo(background_tasks: BackgroundTasks, text: str = Form(...), response_url: str = Form(...)):
    vin = text.strip()
    background_tasks.add_task(fetch_vehicle, vin, response_url)
    return {"response_type": "ephemeral", "text": "🔍 Buscando vehículo..."}

@router.post("/slack/year")
async def slack_por_anio(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    response_url: str = Form(...)
):
    # Validaciones ultra rápidas (sin llamadas a red)
    year = text.strip()
    
    if not year.isdigit():
        return {"text": "Escribe un año válido."}

    # Agendar la tarea pesada
    background_tasks.add_task(fetch_vehicles_by_year, year, response_url)

    # RESPUESTA INMEDIATA (Esto evita el operation_timeout)
    return {
        "response_type": "ephemeral",
        "text": f"🔎 Procesando búsqueda para el año {year}..."
    }

@router.get("/slack/oauth/callback")
def slack_oauth_callback():
    return {"status": "ok"}