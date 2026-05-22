# generators/generate_dataset.py

import os
import csv
from datetime import datetime
from .normal_generator import generate_normal_dataset
from .anomaly_generator import generate_anomaly_dataset


OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_full_dataset(
        normal_count: int,
        anomaly_count: int,
        filename: str = None
):
    """Skapar en CSV med både normal och anomal data."""

    if filename is None:
        filename = f"alarms_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    filepath = os.path.join(OUTPUT_DIR, filename)

    start_time = datetime.now()

    normal_data = generate_normal_dataset(normal_count, start_time)
    anomaly_data = generate_anomaly_dataset(anomaly_count, start_time)

    all_events = normal_data + anomaly_data

    # Sortera efter tid
    all_events.sort(key=lambda e: e.timestamp)

    # Spara till CSV
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_events[0].to_dict().keys()))
        writer.writeheader()

        for event in all_events:
            writer.writerow(event.to_dict())

    print(f"Dataset genererat: {filepath}")
    return filepath
