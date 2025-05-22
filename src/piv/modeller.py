import pandas as pd
import numpy as np
import joblib
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

class Modeller:
    def __init__(self, model_path="src/piv/static/models/model.pkl"):
        self.model_path = model_path
        self.model = LinearRegression()

    def entrenar(self, df: pd.DataFrame, feature_col="close_samsung", target_col="close_samsung"):
        """
        Entrena un modelo de regresión lineal con un retraso de una unidad temporal y guarda el modelo.
        """
        df = df.copy()

        if feature_col not in df.columns:
            raise ValueError(f"La columna '{feature_col}' no existe en el DataFrame")

        df["target"] = df[feature_col].shift(-1)
        df.dropna(inplace=True)

        X = df[[feature_col]]
        y = df["target"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        self.model.fit(X_train, y_train)

        # Guardar el modelo
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)

        # Métricas
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)


        print(f"Modelo entrenado y guardado en {self.model_path}")
        print(f"RMSE: {rmse:.4f}")
        print(f"MAE: {mae:.4f}")

    def predecir(self, datos: pd.DataFrame, col="close"):
        """
        Carga el modelo desde disco y realiza predicciones.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo no encontrado en {self.model_path}")

        model = joblib.load(self.model_path)

        if col not in datos.columns:
            raise ValueError(f"La columna '{col}' no está en el DataFrame.")

        return model.predict(datos[[col]])

