from collector import DataCollector
from enricher import enriquecer_datos
from modeller import Modeller


if __name__ == "__main__":
    collector = DataCollector()
    df = collector.fetch_data()
    df = enriquecer_datos(df)
    modeller = Modeller()
    modeller.entrenar(df)
    collector.update_csv(df)
    collector.update_sqlite(df)
