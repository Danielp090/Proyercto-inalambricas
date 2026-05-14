import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="Bus Cuenca - Daniel Peralta", layout="wide")

# Tu diseño de CSS que está quedando excelente
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #000000 !important; font-weight: bold; font-size: 3rem; }
    [data-testid="stMetricLabel"] { color: #000000 !important; }
    .stMetric { 
        background-color: #ffffff !important; 
        border: 1px solid #d1d1d1; 
        border-radius: 10px; 
        padding: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Función de resaltado para la tabla
def resaltar_rechazo(row):
    # Buscamos la columna 'tipo' (en minúsculas como sale en tu imagen)
    val = str(row.get('tipo', '')).upper()
    color = 'color: #ff4b4b; font-weight: bold' if 'RECHAZADO' in val else 'color: white'
    return [color] * len(row)

st.title("Gestión de Transporte Urbano")

if os.path.exists("../bus_data.json"):
    with open("../bus_data.json", "r") as f:
        db = json.load(f)

    uid = st.text_input("Ingrese o escanee el UID de la tarjeta:").upper().strip()

    if uid in db:
        user = db[uid]
        saldo = user["saldo"]

        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Saldo Disponible", f"${saldo:.2f}")
        
        with c2:
            if saldo <= -0.35:
                st.error(f" ESTADO: RECHAZADO (Límite alcanzado)")
                st.info("La tarjeta no permite más cobros. Saldo mínimo: -$0.35")
            elif saldo < 0:
                st.warning(" ESTADO: SALDO DE EMERGENCIA ACTIVO")
            else:
                st.success(" ESTADO: TARJETA ACTIVA")

        st.subheader("Historial de Movimientos")
        if user["historial"]:
            df = pd.DataFrame(user["historial"])
            # Aplicamos el estilo de color rojo a los rechazos
            st.dataframe(df.style.apply(resaltar_rechazo, axis=1), use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Reporte de Transacciones", csv, f"reporte_{uid}.csv", "text/csv")
    elif uid:
        st.error("Tarjeta no registrada.")
else:
    st.info("Esperando primera transacción...")