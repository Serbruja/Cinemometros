import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control de Cinemómetros", page_icon="⚖️")

# --- CARÁTULA INFORMATIVA ---
st.title("⚖️ Verificador de Cinemómetros")
st.subheader("Guía de Validez de Fotomultas")

with st.expander("📄 MARCO LEGAL Y REQUISITOS DE VALIDEZ (Leer antes de buscar)"):
    st.markdown("""
    ### 1. Requisitos que debe tener el Acta
    Para que una multa sea válida, el acta que recibió debe detallar obligatoriamente:
    * **Marca y Modelo** del radar.
    * **Número de Serie** del equipo.
    * **Fecha de última calibración** (no debe superar el año de antigüedad).

    ### 2. Margen de Tolerancia
    Según la Ley Nacional de Metrología y normas del INTI, los radares tienen un margen de error. En Argentina, la tolerancia general es del **10%** o de **7 km/h** (dependiendo de la zona y el equipo). Si su exceso está dentro de ese margen, la multa no debería proceder.

    ### 3. Coincidencia de Datos
    Los datos del acta **deben coincidir exactamente** con este listado oficial. 
    * Si la Marca/Modelo es correcta pero el Número de Serie no corresponde a ese modelo, **el acta no tiene validez**.
    * Si el equipo está vigente pero los datos en el papel difieren de lo registrado aquí, es motivo de impugnación.
    
    *Vigencia de verificación: 1 (UN) año.*
    """)

st.markdown("---")
@st.cache_data
def cargar_datos():
    try:
        # Cargamos el archivo completo
        df = pd.read_excel("Cinemometros-2025.xlsx")
        
        # Buscamos la fila donde realmente empiezan los datos
        # Buscamos la palabra 'MARCA' en las primeras 20 filas
        for i in range(20):
            if df.iloc[i].astype(str).str.contains('MARCA', case=False).any():
                # Re-cargamos saltando esas filas y tomando la siguiente como cabecera
                df = pd.read_excel("Cinemometros-2025.xlsx", skiprows=i+1)
                break
        
        # Limpieza profunda de columnas
        df.columns = [str(c).strip().upper().replace('.', '') for c in df.columns]
        
        # Estandarizamos fechas
        for col in df.columns:
            if 'FECHA' in col:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df = df.rename(columns={col: 'FECHA_LIMPIA'})
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return None

# Inicializamos variables para evitar NameError
col_serie = col_marca = col_modelo = col_lugar = None

df = cargar_datos()

if df is not None:
    # Identificamos columnas por palabras clave
    for c in df.columns:
        if 'SERIE' in c: col_serie = c
        if 'MARCA' in c: col_marca = c
        if 'MODELO' in c: col_modelo = c
        if 'LUGAR' in c or 'INSTALACION' in c: col_lugar = c

    st.write("### 🔎 Búsqueda de Equipo")
    entrada = st.text_input("Ingrese el número de serie (ej: NEO-0122):", key="search_input")

    if entrada:
        if col_serie:
            # Filtramos
            filtro = df[col_serie].astype(str).str.contains(entrada.strip(), case=False, na=False)
            coincidencias = df[filtro]

            if not coincidencias.empty:
                series_unicas = [str(x) for x in coincidencias[col_serie].unique().tolist()]
                seleccion = st.selectbox("Seleccione el número exacto:", ["-- Seleccione --"] + series_unicas)

                if seleccion != "-- Seleccione --":
                    # Traemos el registro más reciente
                    detalle = coincidencias[coincidencias[col_serie].astype(str) == seleccion].sort_values(by='FECHA_LIMPIA', ascending=False).iloc[0]
                    
                    st.success(f"✅ Datos de: {seleccion}")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Marca:** {detalle.get(col_marca, 'S/D')}")
                        st.write(f"**Modelo:** {detalle.get(col_modelo, 'S/D')}")
                    with c2:
                        f_raw = detalle.get('FECHA_LIMPIA')
                        f_verif = f_raw.strftime('%d/%m/%Y') if pd.notnull(f_raw) else "S/D"
                        st.write(f"**Verificación:** {f_verif}")

                    st.info(f"📍 **Ubicación:** {detalle.get(col_lugar, 'S/D')}")

                    if pd.notnull(f_raw):
                        dias = (datetime.now() - f_raw).days
                        if dias > 365:
                            st.error(f"🚨 VENCIDO: Expiró hace {dias - 365} días.")
                        else:
                            st.success(f"✔️ VIGENTE: Quedan {365 - dias} días.")
            else:
                st.warning("⚠️ No se encontraron coincidencias para ese número.")
        else:
            st.error("No se pudo detectar la columna de Número de Serie.")
else:
    st.error("No se pudo cargar la base de datos.")
