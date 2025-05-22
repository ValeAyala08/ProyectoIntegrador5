import os
import streamlit as st
import pandas as pd
import sys
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Añadir path raíz para importar módulos personalizados
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.piv.collector import DataCollector

CSV_PATH = "src/piv/static/data/data_dashboard.csv"

# Descargar datos si no existe el CSV
if not os.path.exists(CSV_PATH):
    st.info("📥 Archivo no encontrado. Descargando datos de Samsung desde Yahoo Finance...")
    collector = DataCollector(csv_path=CSV_PATH)
    collector.fetch_data_and_save()
    st.success("✅ Datos descargados y guardados en 'data_dashboard.csv'.")

@st.cache_data
def cargar_datos(path):
    df = pd.read_csv(path, parse_dates=["date"], index_col="date")
    return df

df = cargar_datos(CSV_PATH)

# Detectar columna de cierre de Samsung
close_cols = [col for col in df.columns if "close" in col.lower()]
if not close_cols:
    st.error("❌ No se encontró ninguna columna que contenga 'close'.")
    st.stop()

# Tomar la primera columna que coincida como cierre de Samsung
df.rename(columns={close_cols[0]: "close_samsung"}, inplace=True)

if "close_samsung" not in df.columns:
    st.error("❌ La columna 'close_samsung' no está disponible.")
    st.stop()

# ---- DASHBOARD ----
st.title("📊 Dashboard de Samsung (005930.KS)")
st.subheader("🔎 Indicadores Clave")

col1, col2, col3 = st.columns(3)

precio_actual = df['close_samsung'].iloc[-1]
media_movil_7 = df['close_samsung'].rolling(7).mean().iloc[-1]
volatilidad_30 = df['close_samsung'].rolling(30).std().iloc[-1]

col1.metric("💰 Precio Actual", f"{precio_actual:,.2f} ₩")
col2.metric("📈 Media Móvil 7 días", f"{media_movil_7:,.2f} ₩")
col3.metric("📊 Volatilidad 30 días", f"{volatilidad_30:,.2f}")

# Indicadores adicionales
df["retorno_diario"] = df["close_samsung"].pct_change()
df["retorno_acumulado"] = (1 + df["retorno_diario"]).cumprod()
df["variacion_diaria_%"] = df["retorno_diario"].fillna(0) * 100

st.subheader("📉 Indicadores adicionales")
col4, col5 = st.columns(2)

retorno_acum_final = (df['retorno_acumulado'].iloc[-1] - 1) * 100
variacion_diaria_final = df['variacion_diaria_%'].iloc[-1]

col4.metric("📈 Retorno Acumulado", f"{retorno_acum_final:.2f} %")
col5.metric("🔄 Variación Diaria", f"{variacion_diaria_final:.2f} %")

# Gráficos
st.subheader("📊 Evolución del Precio de Cierre de Samsung")
st.line_chart(df["close_samsung"])

df["media_movil_30"] = df["close_samsung"].rolling(30).mean()
st.subheader("📉 Precio y Media Móvil 30 días")
st.line_chart(df[["close_samsung", "media_movil_30"]])

st.subheader("🔁 Retorno Acumulado")
st.line_chart(df["retorno_acumulado"])

st.subheader("📉 Volatilidad Histórica (30 días)")

# Asegúrate de recalcular si no lo hiciste antes
df["volatilidad_30d"] = df["close_samsung"].rolling(30).std()

st.line_chart(df["volatilidad_30d"])

st.subheader("📈 Predicción con ARIMA y SARIMA")

# Usar solo datos no nulos y recientes
serie = df["close_samsung"].dropna()

# ------- ARIMA -------
try:
    st.markdown("### 🔮 Predicción ARIMA")
    model_arima = ARIMA(serie, order=(5, 1, 0))  # p,d,q
    result_arima = model_arima.fit()
    pred_arima = result_arima.forecast(steps=30)  # próximos 30 días

    fig1, ax1 = plt.subplots()
    serie.plot(ax=ax1, label="Histórico")
    pred_arima.plot(ax=ax1, label="ARIMA (30 días)", color="red")
    ax1.legend()
    st.pyplot(fig1)

except Exception as e:
    st.warning(f"No se pudo ajustar ARIMA: {e}")

# ------- SARIMA -------
try:
    st.markdown("### 🌐 Predicción SARIMA")
    model_sarima = SARIMAX(serie, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    result_sarima = model_sarima.fit(disp=False)
    pred_sarima = result_sarima.forecast(steps=30)

    fig2, ax2 = plt.subplots()
    serie.plot(ax=ax2, label="Histórico")
    pred_sarima.plot(ax=ax2, label="SARIMA (30 días)", color="green")
    ax2.legend()
    st.pyplot(fig2)

except Exception as e:
    st.warning(f"No se pudo ajustar SARIMA: {e}")
