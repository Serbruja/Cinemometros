import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control de Cinemómetros", page_icon="⚖️")

st.title("⚖️ Verificador de Cinemómetros")

@st.cache_data
def cargar_datos():
    df = pd.read_excel("Cinemometros-2025.xlsx", skiprows=13)
    # Limpiamos los nombres de todas las columnas: todo a mayúsculas y sin espacios
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Buscamos la columna de fecha (que puede llamarse distinto) y la estandarizamos
    for col in df.columns:
        if 'FECHA' in col:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df = df.rename(columns={col: 'FECHA_LIMPIA'})
            break
    return df

try:
    df = cargar_datos()
    
    # Identificamos las columnas dinámicamente para evitar el KeyError
    col_serie = next((c for c in df.columns if 'SERIE' in c), None)
    col_marca = next((c for c in df.columns if 'MARCA' in c), None)
    col_modelo = next((c for c in df.columns if 'MODELO' in c), None)
    col_lugar = next((c for c in df.columns if 'LUGAR' in c), None)

    entrada = st.text_input("Ingrese el número de serie (ej: NEO-0122):")

    if entrada and col_serie:
        filtro = df[col_serie].astype(str).str.contains(entrada.strip(), case=False, na=False)
        coincidencias = df[filtro]

        if not coincidencias.empty:
            series_unicas = coincidencias[col_serie].unique().tolist()
            seleccion = st.selectbox("Seleccione el número exacto:", ["-- Seleccione --"] + series_unicas)

            if seleccion != "-- Seleccione --":
                detalle = coincidencias[coincidencias[col_serie] == seleccion].sort_values(by='FECHA_LIMPIA', ascending=False).iloc[0]
                
                st.success(f"✅ Datos de: {seleccion}")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Marca:** {detalle.get(col_marca, 'No disponible')}")
                    st.write(f"**Modelo:** {detalle.get(col_modelo, 'No disponible')}")
                with c2:
                    f_verif = detalle['FECHA_LIMPIA'].strftime('%d/%m/%Y') if pd.notnull(detalle['FECHA_LIMPIA']) else "S/D"
                    st.write(f"**Verificación:** {f_verif}")

                st.info(f"📍 **Ubicación:** {detalle.get(col_lugar, 'No disponible')}")

                if pd.notnull(detalle['FECHA_LIMPIA']):
                    dias = (datetime.now() - detalle['FECHA_LIMPIA']).days
                    if dias > 365:
                        st.error(f"🚨 VENCIDO: Expiró hace {dias - 365} días.")
                    else:
                        st.success(f"✔️ VIGENTE: Quedan {365 - dias} días.")
        else:
            st.error("❌ NO EXISTE DATO ALGUNO.")
    else:
        if not col_serie:
            st.error("No se encontró la columna de Número de Serie en el archivo.")

except Exception as e:
    st.error(f"Error técnico: {e}")
