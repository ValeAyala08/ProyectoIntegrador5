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
    print("Columnas en df:", df.columns.tolist())

     #Verificar que exista una columna con "close" y renombrarla
    close_cols = [col for col in df.columns if "close" in col.lower()]
    if close_cols:
        df.rename(columns={close_cols[0]: "close_samsung"}, inplace=True)
    else:
        raise KeyError(f"No se encontró ninguna columna que contenga 'close'. Columnas disponibles: {df.columns.tolist()}")

    # Variables adicionales
    df["rolling_mean_7"] = df["close_samsung"].rolling(7).mean()
    df["return"] = df["close_samsung"].pct_change()
    df["volatility_7"] = df["return"].rolling(7).std()
    df["return_cum"] = (1 + df["return"].fillna(0)).cumprod()

    return df
