import os
import streamlit as st
import pandas as pd
import sys

# Añade el path raíz para importar tu módulo DataCollector
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.piv.collector import DataCollector

CSV_PATH = "src/piv/static/data/data_dashboard.csv"

# Descargar datos si no existe el CSV
if not os.path.exists(CSV_PATH):
     st.info("Archivo de datos no encontrado. Descargando datos desde Yahoo Finance...")
     collector = DataCollector(csv_path=CSV_PATH)
     collector.fetch_data_and_save() # Asumiendo que 'run' cambió a este método o reemplázalo por el correcto
     st.success("Datos generados y guardados en data/btc_eur.csv.")

@st.cache_data
def cargar_datos(path):
     df = pd.read_csv(path, parse_dates=["date"], index_col="date")
     return df

df = cargar_datos(CSV_PATH)

if "close_btc-eur" not in df.columns:
    st.error("La columna 'close' no está en el CSV.")
    st.stop()

st.title("📊 Dashboard")
st.subheader("Indicadores Clave (KPIs)")

col1, col2, col3 = st.columns(3)

precio_actual = df['close_btc-eur'].iloc[-1]
media_movil_7 = df['close_btc-eur'].rolling(7).mean().iloc[-1]
volatilidad_30 = df['close_btc-eur'].rolling(30).std().iloc[-1]

col1.metric("💰 Precio Actual", f"{precio_actual:,.2f} €")
col2.metric("📈 Media Móvil 7 días", f"{media_movil_7:,.2f} €")
col3.metric("📊 Volatilidad 30 días", f"{volatilidad_30:,.2f} €")

# Cálculos adicionales con control de tamaño de datos
df["retorno_diario"] = df["close_btc-eur"].pct_change()
df["retorno_acumulado"] = (1 + df["retorno_diario"]).cumprod()

# Variación diaria en porcentaje, con NaN a 0 para mejor display
df["variacion_diaria_%"] = df["retorno_diario"].fillna(0) * 100

st.subheader("📉 Indicadores adicionales")
col4, col5 = st.columns(2)

retorno_acum_final = (df['retorno_acumulado'].iloc[-1] - 1) * 100
variacion_diaria_final = df['variacion_diaria_%'].iloc[-1]

col4.metric("📈 Retorno Acumulado", f"{retorno_acum_final:.2f} %")
col5.metric("🔄 Variación Diaria", f"{variacion_diaria_final:.2f} %")

st.subheader("📊 Evolución del Precio de Cierre")
st.line_chart(df["close_btc-eur"])

st.subheader("📉 Precio y Media Móvil 30 días")
df["media_movil_30"] = df["close_btc-eur"].rolling(30).mean()
st.line_chart(df[["close_btc-eur", "media_movil_30"]])

st.subheader("🔁 Retorno Acumulado")
st.line_chart(df["retorno_acumulado"])