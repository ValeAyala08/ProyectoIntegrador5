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
                self.logger.warning("Yahoo Finance devolvió un DataFrame vacío.")
                return pd.DataFrame()

            df.reset_index(inplace=True)

            if isinstance(df.columns, pd.MultiIndex):
                self.logger.warning("Se detectaron columnas con MultiIndex. Aplanando...")
                df.columns = ['_'.join(filter(None, map(str, col))).lower() for col in df.columns]
            else:
                df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]

            self.logger.info(f"{len(df)} filas descargadas.")
            self.logger.debug(f"Columnas resultantes: {df.columns.tolist()}")
            return df

        except Exception as e:
            self.logger.error(f"Error al descargar los datos: {e}")
            return pd.DataFrame()

    def update_csv(self, df):
        if df.empty:
            self.logger.warning("No hay datos para guardar en el CSV.")
            return

        if 'date' not in df.columns:
            self.logger.error(f"La columna 'date' no está presente en el DataFrame: columnas = {df.columns.tolist()}")
            return

        self.logger.debug(f"Primeras filas del DataFrame nuevo:\n{df.head()}")
        self.logger.debug(f"Columnas del DataFrame nuevo: {df.columns.tolist()}")

        try:
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

            if os.path.exists(self.csv_path):
                try:
                    existing = pd.read_csv(self.csv_path)

                    if 'date' not in existing.columns:
                        self.logger.warning("El CSV existente no contiene la columna 'date'. Se sobrescribirá.")
                        merged = df
                    else:
                        merged = pd.concat([existing, df]).drop_duplicates(subset="date").sort_values(by="date")
                        self.logger.info("Hay un CSV existente. Fusionando.")
                except Exception as e:
                    self.logger.error(f"Error al leer el CSV existente: {e}")
                    merged = df
            else:
                self.logger.warning("Archivo CSV no encontrado. Se creará uno nuevo.")
                merged = df

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
