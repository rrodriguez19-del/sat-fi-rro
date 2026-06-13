import streamlit as st
import requests
import pandas as pd

# Configuración de la interfaz gráfica
st.set_page_config(page_title="SAT-FI // Antufen-Uwafen-Kramberries", page_icon="🌱", layout="wide")

# Título y Encabezado principal de la plataforma
st.title("🌱 SAT-FI: Sistema de Alerta Temprana Fitosanitaria Inteligente")
st.markdown("### Plataforma de Monitoreo Híbrido para la Producción de Semillas de Alta Pureza")
st.markdown("---")

# 1. BARRA LATERAL: Configuración del Huerto y Cultivo
st.sidebar.header("⚙️ Configuración del Monitoreo")
region = st.sidebar.selectbox(
    "Ubicación del Huerto Piloto:",
    ["Región de La Araucanía (Sede Sur)", "Región del Maule", "Región de O'Higgins"]
)

grupo_cultivo = st.sidebar.selectbox(
    "Seleccione el Grupo de Cultivo:",
    ["Brásicas", "Espinacas", "Asteráceas (Lechuga y Radicchio)"]
)

# Diccionario dinámico fitosanitario con tus 17 variables solicitadas
base_fitosanitaria = {
    "Brásicas": {
        "Enfermedades": [
            "Xanthomonas campestris (Pudrición negra - CRÍTICA)", 
            "Alternaria spp. (Mancha negra)", 
            "Peronospora parasitica (Mildiú)", 
            "Botrytis cinerea (Pudrición gris)", 
            "Sclerotinia sclerotiorum (Pudrición blanca)", 
            "Erwinia carotovora (Pudrición blanda)"
        ],
        "Plagas": [
            "Plutella xylostella (Polilla de las brásicas)", 
            "Pulgón de las brásicas (Brevicoryne brassicae)", 
            "Pulgón verde (Myzus persicae)", 
            "Mosquita blanca", 
            "Arañita roja"
        ]
    },
    "Espinacas": {
        "Enfermedades": [
            "Verticillium dahliae (Marchitez)", 
            "Fusarium oxysporum (Fusariosis)", 
            "Botrytis cinerea (Pudrición gris)", 
            "Otras enfermedades fúngicas"
        ],
        "Plagas": [
            "Pulgones (Vectores de virus)", 
            "Arañita roja", 
            "Otras plagas de la hoja"
        ]
    },
    "Asteráceas (Lechuga y Radicchio)": {
        "Enfermedades": [
            "Sclerotinia sclerotiorum", 
            "Botrytis cinerea", 
            "Viosis (Complejo de Virus)"
        ],
        "Plagas": [
            "Pulgones", 
            "Mosquita blanca"
        ]
    }
}

tipo_monitoreo = st.sidebar.radio("Tipo de Objetivo Fitosanitario:", ["Enfermedades", "Plagas"])
objetivo_especifico = st.sidebar.selectbox(
    f"Seleccione {tipo_monitoreo.lower()} a evaluar:",
    base_fitosanitaria[grupo_cultivo][tipo_monitoreo]
)

# Coordenadas geográficas automáticas para las llamadas de la API de clima
coords = {"Lat": -38.7397, "Lon": -72.5984} # Por defecto Temuco, Araucanía
if "Maule" in region: 
    coords = {"Lat": -35.4264, "Lon": -71.6554}
elif "O'Higgins" in region: 
    coords = {"Lat": -34.1708, "Lon": -70.7444}

# Interfaz manual interactiva para emular los Dataloggers físicos de la empresa
st.sidebar.markdown("---")
st.sidebar.subheader("📡 Parámetros del Datalogger Propio")
st.sidebar.info("Simulación activa de lectura en tiempo real.")
dl_temp = st.sidebar.slider("Temperatura Datalogger (°C)", min_value=5.0, max_value=35.0, value=22.0, step=0.5)
dl_hum = st.sidebar.slider("Humedad Relativa Datalogger (%)", min_value=30, max_value=100, value=85, step=1)

# 2. CONEXIÓN EN TIEMPO REAL CON LA API METEOROLÓGICA (Macroclima)
@st.cache_data(ttl=600)
def obtener_clima_api(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m&hourly=temperature_2m,relative_humidity_2m&forecast_days=3"
    try: 
        return requests.get(url).json()
    except: 
        return None

clima_data = obtener_clima_api(coords["Lat"], coords["Lon"])

# 3. ALGORITMO FITOSANITARIO: Matriz lógica de evaluación de riesgos
riesgo = "Bajo"
color_alerta = "green"
recomendacion = "✅ Condiciones estables. Continuar con el esquema de monitoreo rutinario."

if tipo_monitoreo == "Enfermedades":
    if "Xanthomonas" in objetivo_especifico:
        if dl_temp >= 24.0 and dl_hum >= 75:
            riesgo = "Alto"
            color_alerta = "red"
            recomendacion = "⚠️ ALERTA CRÍTICA: Xanthomonas campestris requiere calor y humedad para su multiplicación bacteriana. Riesgo extremo de transmisión sistémica en semilla de brásica. Evitar labores mecánicas con rocío."
        elif dl_temp >= 20.0 or dl_hum >= 70:
            riesgo = "Medio"
            color_alerta = "orange"
            recomendacion = "⚠️ ADVERTENCIA: Temperaturas templadas. Inspeccionar selectivamente plantas con síntomas de 'V' necróticas en los bordes de las hojas."
    elif "Alternaria" in objetivo_especifico or "Botrytis" in objetivo_especifico:
        if dl_hum >= 80 and (15.0 <= dl_temp <= 22.0):
            riesgo = "Alto"
            color_alerta = "red"
            recomendacion = f"⚠️ ALERTA CRÍTICA: Alta presión para {objetivo_especifico}. Condición predisponente para pudrición de capítulos florales y silicuas. Proteja la viabilidad de la semilla."
        elif dl_hum >= 70:
            riesgo = "Medio"
            color_alerta = "orange"
    elif "Mildiú" in objetivo_especifico or "Peronospora" in objetivo_especifico:
        if dl_hum >= 85 and (8.0 <= dl_temp <= 16.0):
            riesgo = "Alto"
            color_alerta = "red"
            recomendacion = "⚠️ ALERTA CRÍTICA: El Mildiú progresa velozmente en condiciones de frío húmedo. Riesgo de colonización vegetativa."
        elif dl_hum >= 75: 
            riesgo = "Medio"
            color_alerta = "orange"
    elif "Sclerotinia" in objetivo_especifico:
        if dl_hum >= 85 and (12.0 <= dl_temp <= 20.0):
            riesgo = "Alto"
            color_alerta = "red"
            recomendacion = "⚠️ ALERTA CRÍTICA: Humedad persistente en el suelo activa los esclerocios. Peligro de colapso de plantas y contaminación del lote de semillas."
        elif dl_hum >= 75: 
            riesgo = "Medio"
            color_alerta = "orange"
    elif "Verticillium" in objetivo_especifico or "Fusarium" in objetivo_especifico:
        if dl_temp >= 22.0:
            riesgo = "Medio"
            color_alerta = "orange"
            recomendacion = "⚠️ ADVERTENCIA: Hongos vasculares incrementan su expresión de síntomas de marchitez con el aumento de la temperatura ambiental por estrés hídrico."
    elif "Virosis" in objetivo_especifico:
        riesgo = "Variable"
        color_alerta = "blue"
        recomendacion = "ℹ️ NOTA: El riesgo de virosis está directamente encadenado a la presión y manejo de vectores (Pulgones/Mosquita Blanca). Evaluar la pestaña de plagas."
else:
    if "Plutella" in objetivo_especifico:
        if dl_temp >= 20.0: 
            riesgo = "Alto"
            color_alerta = "red"
            recomendacion = "⚠️ ALERTA CRÍTICA: Altas temperaturas aceleran el ciclo biológico de Plutella xylostella. Las larvas pueden dañar directamente las inflorescencias de la semilla. Revisar posturas de huevos."
        elif dl_temp >= 15.0: 
            riesgo = "Medio"
            color_alerta = "orange"
    elif "Pulgón" in objetivo_especifico or "Pulgones" in objetivo_especifico:
        if 18.0 <= dl_temp <= 25.0 and dl_hum <= 70: 
            riesgo = "Alto"
            color_alerta = "red"
            recomendacion = "⚠️ ALERTA CRÍTICA: Condiciones óptimas para el crecimiento exponencial de colonias de áfidos. Alto riesgo de transmisión de virus no persistentes."
        elif 15.0 <= dl_temp <= 28.0: 
            riesgo = "Medio"
            color_alerta = "orange"
    elif "Arañita roja" in objetivo_especifico:
        if dl_temp >= 26.0 and dl_hum <= 55: 
            riesgo = "Alto"
            color_alerta = "red"
            recomendacion = "⚠️ ALERTA CRÍTICA: Ambiente seco y cálido (baja humedad y alta temperatura) gatilla explosión de Arañita roja. Monitorear focos perimetrales."
        elif dl_temp >= 20.0: 
            riesgo = "Medio"
            color_alerta = "orange"
    elif "Mosquita blanca" in objetivo_especifico:
        if dl_temp >= 22.0: 
            riesgo = "Alto"
            color_alerta = "red"
            recomendacion = "⚠️ ALERTA CRÍTICA: Alta presión de mosquita blanca. Controlar focos para evitar la acumulación de miellada que favorece la fumagina."
        else: 
            riesgo = "Medio"
            color_alerta = "orange"

# 4. DESPLIEGUE VISUAL DEL DASHBOARD INTERACTIVO
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Monitoreo del Microclima (Datalogger)")
    mc1, mc2 = st.columns(2)
    mc1.metric("Temperatura Cuartel", f"{dl_temp} °C")
    mc2.metric("Humedad Relativa", f"{dl_hum} %")
    
    st.markdown(f"🤖 Evaluación para: **{objetivo_especifico}**")
    st.markdown(f"<h1 style='color:{color_alerta}; text-align:center; background-color:#f0f2f6; padding:10px; border-radius:10px;'>RIESGO {riesgo.upper()}</h1>", unsafe_url_allowed=True)

with col2:
    st.subheader("🌐 Predicción del Macroclima (API Abierta)")
    if clima_data:
        st.write(f"**Predicción para:** {region}")
        st.write(f"Temperatura exterior actual: {clima_data['current']['temperature_2m']} °C")
        st.write(f"Humedad exterior actual: {clima_data['current']['relative_humidity_2m']} %")
        
        # Tabla corta de tendencias horarias
        df_api = pd.DataFrame({
            "Hora sugerida": clima_data["hourly"]["time"][:4],
            "Temperatura (°C)": clima_data["hourly"]["temperature_2m"][:4],
            "Humedad (%)": clima_data["hourly"]["relative_humidity_2m"][:4]
        })
        st.dataframe(df_api, use_container_width=True)
    else:
        st.error("Error al conectar con la API de predicción climática.")

st.markdown("---")
st.subheader("📋 Criterio Técnico y Recomendación Operativa")
st.warning(recomendacion)

st.caption("SAT-FI v2.0 // Optimización y reportabilidad de fitosanitarios para semilleros corporativos.")
