import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# Configuración estética de la página
st.set_page_config(
    page_title="Sistema de Transporte Cuenca",
    page_icon="🚌",
    layout="wide"
)

# Estilo personalizado con CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_stdio=True)

# Título y encabezado
st.title("🚌 Sistema Inteligente de Gestión de Transporte")
st.subheader("Consulta de Saldo y Transacciones - Red IoT Cuenca")
st.markdown("---")

# Función para cargar datos
def cargar_base_datos():
    if os.path.exists("bus_data.json"):
        with open("bus_data.json", "r") as f:
            return json.load(f)
    return None

db = cargar_base_datos()

if db:
    # --- BARRA LATERAL (Estadísticas generales) ---
    with st.sidebar:
        st.header("📊 Resumen del Sistema")
        total_tarjetas = len(db)
        st.write(f"Tarjetas registradas: **{total_tarjetas}**")
        if st.button("🔄 Actualizar Datos"):
            st.rerun()

    # --- CUERPO PRINCIPAL ---
    # Buscador con autocompletado simulado
    search_uid = st.text_input("🔍 Ingrese el UID de su tarjeta:", help="Ejemplo: A1 B2 C3 D4").upper().strip()

    if search_uid:
        if search_uid in db:
            usuario = db[search_uid]
            
            # Fila de métricas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # El saldo se pone rojo si es bajo
                saldo = usuario['saldo']
                st.metric("Saldo Disponible", f"${saldo:.2f}", delta=None, delta_color="normal")
            
            with col2:
                num_trans = len(usuario['historial'])
                st.metric("Movimientos Registrados", num_trans)
            
            with col3:
                ultima_act = usuario['historial'][0]['fecha'] if num_trans > 0 else "N/A"
                st.write(f"**Última actividad:**  \n{ultima_act}")

            st.markdown("### 📋 Historial de los últimos 10 movimientos")
            
            if num_trans > 0:
                # Convertir historial a DataFrame para mejor visualización
                df = pd.DataFrame(usuario["historial"])
                
                # Renombrar columnas para la tabla
                df.columns = ["Fecha y Hora", "Tipo de Operación", "Monto"]
                
                # Mostrar tabla con estilo
                st.dataframe(df, use_container_width=True)

                # Botón para descargar el reporte (Plus para la tesis)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Reporte de Transacciones (CSV)",
                    data=csv,
                    file_name=f"reporte_{search_uid}.csv",
                    mime="text/csv",
                )
            else:
                st.info("Esta tarjeta aún no cuenta con movimientos registrados.")
        else:
            st.error(f"❌ La tarjeta con UID **{search_uid}** no existe en la base de datos.")
    else:
        st.info("💡 Consejo: Acerque su tarjeta al lector en el bus para verla reflejada aquí al instante.")

else:
    st.warning("📡 No se detectan datos en el servidor. Realice una transacción con el ESP32 para inicializar el sistema.")

# Pie de página
st.markdown("---")
st.caption("Proyecto de Tesis - Ingeniería en Electrónica | Cuenca, Ecuador 2026")