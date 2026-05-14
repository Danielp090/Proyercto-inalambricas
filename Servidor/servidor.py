from fastapi import FastAPI, Request
import json
import os
from datetime import datetime

app = FastAPI()
# El archivo se guardará en la carpeta raíz del proyecto
DB_FILE = "../bus_data.json"

def actualizar_base_datos(datos):
    """Procesa la lógica de saldo y guarda el historial."""
    # 1. Leer la base de datos existente o crear una nueva
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = {}
    else:
        db = {}

    uid = datos["uid"]
    
    # 2. Si el usuario es nuevo, inicializar su perfil
    if uid not in db:
        db[uid] = {"saldo": 0.0, "historial": []}

    # 3. Actualizar saldo según la acción enviada por el ESP32-C3
    monto = datos["monto"]
    if datos["accion"] == "cobro":
        db[uid]["saldo"] -= monto
    elif datos["accion"] == "recarga":
        db[uid]["saldo"] += monto

    # 4. Registrar la transacción con fecha y hora actual
    nueva_transaccion = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": datos["accion"].capitalize(),
        "monto": f"${monto:.2f}"
    }
    
    # Insertar al inicio para que la más reciente aparezca primero
    db[uid]["historial"].insert(0, nueva_transaccion)
    
    # REGLA: Mantener solo las últimas 10 transacciones
    db[uid]["historial"] = db[uid]["historial"][:10]

    # 5. Guardar los cambios de forma persistente
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

@app.post("/api/transaccion")
async def recibir_transaccion(request: Request):
    """Endpoint que recibe el JSON del hardware."""
    try:
        datos = await request.json()
        actualizar_base_datos(datos)
        print(f"✅ Transacción procesada: {datos['accion']} para UID {datos['uid']}")
        return {"status": "success", "message": "Datos guardados correctamente"}
    except Exception as e:
        print(f"❌ Error en el servidor: {str(e)}")
        return {"status": "error", "message": str(e)}

# Comando para ejecutar: uvicorn servidor:app --host 0.0.0.0 --port 8000