from fastapi import FastAPI
from routes.vehicles import router as vehicles_router
from database import get_connection

app = FastAPI(title="Dealer Intelligence API")

# Registrar rutas
app.include_router(vehicles_router)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Crear tabla vehicles si no existe al iniciar
@app.on_event("startup")
def startup_event():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id SERIAL PRIMARY KEY,
        vin VARCHAR(17) UNIQUE NOT NULL,
        year INTEGER,
        make VARCHAR(50),
        model VARCHAR(50),
        trim VARCHAR(50),
        price NUMERIC,
        miles INTEGER,
        dealer_name VARCHAR(100),
        city VARCHAR(50),
        state VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

