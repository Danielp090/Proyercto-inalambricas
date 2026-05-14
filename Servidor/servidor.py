from fastapi import FastAPI, Request
import json
import os
from datetime import datetime

app = FastAPI()
DB_FILE = "../bus_data.json" # Se guarda un nivel arriba para que ambos lo vean

@app.post("/api/transaccion")
async def recibir_datos(request: Request):
    datos = await request.json()
    # Lógica de actualización de saldo e historial...
    return {"status": "ok"}