import streamlit as st
import json
import os
import pandas as pd

# Configuración de la interfaz
st.set_page_config(page_title="Sistema de Buses - Consulta", layout="centered")

# Estilo visual con CSS
st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚌 Monitor de Saldo y Transacciones")
st.write("Ingrese su ID de tarjeta para verificar su estado actual.")
st.markdown("---")

# Ruta al archivo de datos compartido con el backend
DB_PATH = "../bus_data.json"

if os.path.exists(DB_PATH):
    with open(DB_PATH, "r") as f:
        db = json.load(f)

    # Buscador de tarjeta
    uid_busqueda = st.text_input("🔍 UID de la Tarjeta (Ej: A1B2C3D4):").upper().strip()

    if uid_busqueda:
        if uid_busqueda in db:
            usuario = db[uid_busqueda]
            
            # Mostrar métricas destacadas
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Saldo Disponible", value=f"${usuario['saldo']:.2f}")
            with col2:
                st.info(f"ID de Usuario: {uid_busqueda}")

            # Tabla de historial
            st.subheader("📋 Últimos 10 Movimientos")
            if usuario["historial"]:
                df = pd.DataFrame(usuario["historial"])
                # Renombrar para una tabla más limpia
                df.columns = ["Fecha", "Operación", "Valor"]
                st.table(df)
                
                # Botón de descarga para el reporte de tesis
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Historial (CSV)",
                    data=csv,
                    file_name=f"historial_{uid_busqueda}.csv",
                    mime="text/csv",
                )
            else:
                st.write("No hay transacciones registradas para esta tarjeta.")
        else:
            st.error("⚠️ Tarjeta no encontrada en el sistema.")
    else:
        st.info("Esperando ingreso de UID...")
else:
    st.warning("📡 No hay datos registrados aún. Realice una operación en el bus.")

# Comando para ejecutar: streamlit run pagina.py