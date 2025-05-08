from collector import DataCollector

if __name__ == "__main__":
    collector = DataCollector()
    df = collector.fetch_data()
    collector.update_csv(df)
    collector.update_sqlite(df)
