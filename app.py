import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control de Cinemómetros", page_icon="⚖️")

# --- CARÁTULA INFORMATIVA ---
st.title("⚖️ Verificador de Cinemómetros")
with st.expander("📄 Ver Marco Legal e Información del INTI"):
    st.info("""
    **Importante:** Cada equipo tiene un **Número de Serie único**. 
    La validez de la multa depende de que *ese equipo específico* esté verificado.
    * Vigencia: 1 año desde la última verificación.
    """)

@st.cache_data
def cargar_datos():
    # Saltamos las 13 líneas de encabezado
    df = pd.read_excel("Cinemometros-2025.xlsx", skiprows=13)
    df.columns = df.columns.str.strip()
    # Limpiamos nombres de columnas y datos
    if 'FECHA VERIFICACION' in df.columns:
        df['FECHA VERIFICACION'] = pd.to_datetime(df['FECHA VERIFICACION'], errors='coerce')
    return df

try:
    df = cargar_datos()
    
    st.write("### 🔎 Búsqueda por Identificador Único")
    st.caption("Escriba el número de serie que figura en su acta (Ej: NEO-0122, 291, etc.)")

    # Entrada de texto
    entrada = st.text_input("Número de Serie:", placeholder="Ingrese aquí el número...")

    if entrada:
        # Filtramos coincidencias parciales para ayudar al usuario
        filtro = df['NRO. DE SERIE'].astype(str).str.contains(entrada.strip(), case=False, na=False)
        coincidencias = df[filtro]

        if not coincidencias.empty:
            # Agrupamos por Nro de Serie para que en el selector no aparezcan duplicados
            series_unicas = coincidencias['NRO. DE SERIE'].unique().tolist()
            
            seleccion = st.selectbox(
                f"Se encontraron {len(series_unicas)} equipos. Seleccione el exacto:",
                ["-- Seleccione el número de serie --"] + series_unicas
            )

            if seleccion != "-- Seleccione el número de serie --":
                # Buscamos todos los registros de ESE número de serie seleccionado
                registros_equipo = df[df['NRO. DE SERIE'] == seleccion]
                
                # Nos quedamos con el más reciente (por fecha de verificación)
                ultimo_registro = registros_equipo.sort_values(by='FECHA VERIFICACION', ascending=False).iloc[0]
                
                st.markdown("---")
                st.subheader(f"Ficha del Equipo: {seleccion}")
                
                # Mostramos los datos específicos de ESE número de serie
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Identificación:** {ultimo_registro['NRO. DE SERIE']}")
                    st.write(f"**Marca:** {ultimo_registro['MARCA']}")
                    st.write(f"**Modelo:** {ultimo_registro['MODELO']}")
                with col2:
                    st.write(f"**Tipo:** {ultimo_registro['TIPO']}")
                    fecha_v = ultimo_registro['FECHA VERIFICACION'].strftime('%d/%m/%Y') if pd.notnull(ultimo_registro['FECHA VERIFICACION']) else "No informada"
                    st.write(f"**Fecha Verificación:** {fecha_v}")

                st.warning(f"📍 **Ubicación Declarada:** {ultimo_registro['LUGAR DE INSTALACION']}")

                # Lógica de semáforo para la vigencia
                if pd.notnull(ultimo_registro['FECHA VERIFICACION']):
                    dias_pasados = (datetime.now() - ultimo_registro['FECHA VERIFICACION']).days
                    if dias_pasados > 365:
                        st.error(f"🚨 EQUIPO VENCIDO: La verificación expiró hace {dias_pasados - 365} días.")
                    else:
                        st.success(f"✅ EQUIPO HABILITADO: Verificación vigente por {365 - dias_pasados} días más.")
        else:
            st.error("❌ NO EXISTE DATO ALGUNO. El número no coincide con ningún equipo registrado.")

except Exception as e:
    st.error("Error al leer la base de datos. Verifique el archivo Excel.")
