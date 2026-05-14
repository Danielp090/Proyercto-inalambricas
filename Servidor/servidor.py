from fastapi import FastAPI, Request
import json
import os
from datetime import datetime

app = FastAPI()
DB_FILE = "../bus_data.json"

@app.post("/api/transaccion")
async def recibir_transaccion(request: Request):
    try:
        datos = await request.json()
        uid, accion, monto = datos["uid"], datos["accion"], datos["monto"]

        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                db = json.load(f)
        else:
            db = {}

        if uid not in db:
            db[uid] = {"saldo": 0.0, "historial": []}

        usuario = db[uid]
        
        # --- LÓGICA DE VALIDACIÓN ATÓMICA ---
        tipo_final = ""
        monto_final = ""

        if accion == "cobro":
            if (usuario["saldo"] - monto) < -0.35:
                # RECHAZO TOTAL: No se resta dinero
                tipo_final = " RECHAZADO"
                monto_final = "$0.00"
                print(f" BLOQUEO: UID {uid} intentó bajar de -0.35")
            else:
                # APROBADO: Aquí recién restamos
                usuario["saldo"] -= monto
                tipo_final = "Cobro"
                monto_final = f"${monto:.2f}"
        else:
            # RECARGA: Siempre suma
            usuario["saldo"] += monto
            tipo_final = "Recarga"
            monto_final = f"${monto:.2f}"

        # --- REGISTRO CON COLUMNAS EN MINÚSCULAS (Para tu tabla) ---
        nueva_trans = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo_final,
            "monto": monto_final
        }
        
        usuario["historial"].insert(0, nueva_trans)
        usuario["historial"] = usuario["historial"][:10]

        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=4)

        return {"status": "success", "resultado": tipo_final}

    except Exception as e:
        return {"status": "error", "message": str(e)}