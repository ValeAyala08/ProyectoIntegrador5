# src/piv/utils/data_enrichment.py

import pandas as pd
import yfinance as yf

def enriquecer_datos(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "date" not in df.columns:
        return df

    # Asegurarse de que la columna 'date' sea datetime
    df["date"] = pd.to_datetime(df["date"])

    # Descargar S&P 500 para enriquecer con contexto macroeconómico
    sp500 = yf.download("^GSPC", start=df["date"].min().strftime("%Y-%m-%d"),
                        end=df["date"].max().strftime("%Y-%m-%d"),
                        progress=False, auto_adjust=True)
    sp500 = sp500.reset_index()[["Date", "Close"]]
    sp500.columns = ["date", "sp500_close"]

    # Merge externo por fecha
    df = pd.merge(df, sp500, how="left", on="date")


    # Variables adicionales
    df["rolling_mean_7"] = df["close_btc-eur"].rolling(7).mean()
    df["return"] = df["close_btc-eur"].pct_change()
    df["volatility_7"] = df["return"].rolling(7).std()
    df["return_cum"] = (1 + df["return"].fillna(0)).cumprod()

    return df
