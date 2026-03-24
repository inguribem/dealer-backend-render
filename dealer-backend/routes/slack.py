from fastapi import APIRouter, Form
import requests
import os
import re

router = APIRouter()

API_URL = os.getenv("API_URL")

# Regex VIN (sin I, O, Q)
VIN_REGEX = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


def is_valid_vin(vin: str) -> bool:
    return bool(VIN_REGEX.match(vin))


@router.post("/slack/vehicle")
async def slack_vehiculo(text: str = Form(...)):
    vin = text.strip().upper()

    # 🔹 Validación 1: vacío
    if not vin:
        return {
            "response_type": "ephemeral",
            "text": "Debes proporcionar un VIN. Ej: /vehiculo 1HGCM82633A123456"
        }

    # 🔹 Validación 2: formato VIN
    if not is_valid_vin(vin):
        return {
            "response_type": "ephemeral",
            "text": (
                "VIN inválido.\n"
                "Debe tener 17 caracteres y no incluir I, O o Q.\n"
                "Ejemplo válido: 1HGCM82633A123456"
            )
        }

    try:
        response = requests.get(f"{API_URL}/vehicle/{vin}")

        # 🔹 Validación 3: respuesta backend
        if response.status_code == 404:
            return {
                "response_type": "ephemeral",
                "text": f"No se encontró el vehículo con VIN {vin}"
            }

        if response.status_code != 200:
            return {
                "response_type": "ephemeral",
                "text": "Error consultando el servicio. Intenta nuevamente."
            }

        data = response.json()

        return {
            "response_type": "in_channel",
            "text": f"""
🚗 *Reporte de Vehículo*
VIN: {vin}
Estado: {data.get('status')}
Precio: {data.get('price')}
"""
        }

    except Exception as e:
        return {
            "response_type": "ephemeral",
            "text": f"Error técnico: {str(e)}"
        }
    
@router.get("/slack/oauth/callback")
def slack_oauth_callback():
    return {"status": "ok"}