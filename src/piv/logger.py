import logging
import os

def setup_logger(log_path="src/piv/static/data/collector.log"):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger = logging.getLogger("DataCollector")
    logger.setLevel(logging.INFO)

    # Evita duplicación de handlers si se llama múltiples veces
    if not logger.handlers:
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
