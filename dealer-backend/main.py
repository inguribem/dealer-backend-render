from fastapi import FastAPI
from routes import vehicles, auctions, service_orders, catalog, reports, slack
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (IMPORTANTE para Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicles.router)
app.include_router(auctions.router)
app.include_router(service_orders.router)
app.include_router(catalog.router)
app.include_router(reports.router)
app.include_router(slack.router)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}
