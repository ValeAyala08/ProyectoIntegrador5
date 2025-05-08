import yfinance as yf
import pandas as pd
import sqlite3
from logger import setup_logger
import os

class DataCollector:
    def __init__(self, ticker="BTC-EUR", db_path="src/piv/static/data/historical.db", csv_path="src/piv/static/data/historical.csv"):
        self.ticker = ticker
        self.db_path = db_path
        self.csv_path = csv_path
        self.logger = setup_logger()
        self.logger.info(f"Iniciando recolección de datos para {self.ticker}")

    def fetch_data(self):
        try:
            self.logger.info("Descargando los datos desde Yahoo Finance.")
            result = yf.download(self.ticker, period="max", progress=False, threads=False, auto_adjust=True)

            if isinstance(result, tuple):
                self.logger.warning("Se recibió una tupla de yf.download, extrayendo primer elemento.")
                df = result[0]
            else:
                df = result

            if df.empty:
                self.logger.warning("Yahoo Finance devolvió un DataFrame vacío. Puede ser un error temporal o bloqueo.")
                return pd.DataFrame()

            df.reset_index(inplace=True)
            df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
            self.logger.info(f"{len(df)} filas descargadas.")
            return df

        except Exception as e:
            self.logger.error(f"Error al descargar los datos: {e}")
            return pd.DataFrame()

    def update_csv(self, df):
        if df.empty:
            self.logger.warning("No hay datos para guardar en el CSV.")
            return

        try:
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            if os.path.exists(self.csv_path):
                existing = pd.read_csv(self.csv_path)
                merged = pd.concat([existing, df]).drop_duplicates(subset="date")
                self.logger.info("Hay un CSV existente. Fusionando.")
            else:
                merged = df
                self.logger.warning("Archivo CSV no encontrado. Se creará uno nuevo.")

            merged.to_csv(self.csv_path, index=False)
            self.logger.info(f"CSV actualizado. Total: {len(merged)} registros.")
        except Exception as e:
            self.logger.error(f"Error al actualizar CSV: {e}")

    def update_sqlite(self, df):
        if df.empty:
            self.logger.warning("No hay datos para guardar en SQLite.")
            return

        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.logger.info("Conectando a SQLite.")
            with sqlite3.connect(self.db_path) as conn:
                try:
                    existing = pd.read_sql("SELECT * FROM bitcoin_data", conn)
                    merged = pd.concat([existing, df]).drop_duplicates(subset="date")
                    self.logger.info("Hay datos existentes. Fusionando...")
                except Exception:
                    merged = df
                    self.logger.warning("Como la tabla no existe, se creará una nueva.")

                merged.to_sql("bitcoin_data", conn, if_exists="replace", index=False)
                self.logger.info(f"SQLite actualizado. Total: {len(merged)} registros.")
        except Exception as e:
            self.logger.error(f"Error al actualizar SQLite: {e}")
