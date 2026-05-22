# generate_data.py
from generators.generate_dataset import generate_full_dataset

if __name__ == "__main__":
    generate_full_dataset(
        normal_count=500,
        anomaly_count=13
    )
