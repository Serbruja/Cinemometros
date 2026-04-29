import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control de Cinemómetros", page_icon="⚖️")

# --- CARÁTULA INFORMATIVA ---
st.title("⚖️ Verificador de Cinemómetros")
with st.expander("📄 Ver Marco Legal e Información del INTI"):
    st.info("""
    **Importante:** Cada equipo tiene un **Número de Serie único**. 
    La validez de la multa depende de que ese equipo específico esté verificado.
    * Vigencia: 1 año desde la última verificación.
    """)

@st.cache_data
def cargar_datos():
    # Saltamos las 13 líneas de encabezado del archivo original
    df = pd.read_excel("Cinemometros-2025.xlsx", skiprows=13)
    # Limpiamos los nombres de las columnas (quita espacios locos al principio o final)
    df.columns = [str(c).strip() for c in df.columns]
    # Convertimos la fecha
    if 'FECHA VERIFICACION' in df.columns:
        df['FECHA VERIFICACION'] = pd.to_datetime(df['FECHA VERIFICACION'], errors='coerce')
    return df

try:
    df = cargar_datos()
    
    st.write("### 🔎 Búsqueda de Equipo")
    entrada = st.text_input("Ingrese el número de serie (ej: NEO-0122 o 291):")

    if entrada:
        # Buscamos la columna exacta. En tu Excel es 'NRO. DE SERIE'
        columna_serie = 'NRO. DE SERIE' 
        
        if columna_serie in df.columns:
            # Filtramos coincidencias
            filtro = df[columna_serie].astype(str).str.contains(entrada.strip(), case=False, na=False)
            coincidencias = df[filtro]

            if not coincidencias.empty:
                series_unicas = coincidencias[columna_serie].unique().tolist()
                seleccion = st.selectbox("Seleccione el número exacto:", ["-- Seleccione --"] + series_unicas)

                if seleccion != "-- Seleccione --":
                    detalle = coincidencias[coincidencias[columna_serie] == seleccion].sort_values(by='FECHA VERIFICACION', ascending=False).iloc[0]
                    
                    st.success(f"✅ Datos de: {seleccion}")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Marca:** {detalle['MARCA']}")
                        st.write(f"**Modelo:** {detalle['MODELO']}")
                    with c2:
                        f_verif = detalle['FECHA VERIFICACION'].strftime('%d/%m/%Y') if pd.notnull(detalle['FECHA VERIFICACION']) else "S/D"
                        st.write(f"**Verificación:** {f_verif}")

                    st.info(f"📍 **Ubicación:** {detalle['LUGAR DE INSTALACION']}")

                    if pd.notnull(detalle['FECHA VERIFICACION']):
                        dias = (datetime.now() - detalle['FECHA VERIFICACION']).days
                        if dias > 365:
                            st.error(f"🚨 VENCIDO: La verificación expiró hace {dias - 365} días.")
                        else:
                            st.success(f"✔️ VIGENTE: Quedan {365 - dias} días de validez.")
            else:
                st.error("❌ NO EXISTE DATO ALGUNO.")
        else:
            st.error(f"No se encontró la columna '{columna_serie}'. Columnas detectadas: {list(df.columns)}")

except Exception as e:
    st.error(f"Hubo un problema al cargar el Excel: {e}")
