from pathlib import Path
import json
import time
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "api_dataset.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "latest_reading.json"

DELAY_SECONDS = 1


def load_data():
    print("Loading API dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        usecols=[
            "meter_id",
            "timestamp",
            "consumption",
            "classification",
            "confidence_score",
        ],
        parse_dates=["timestamp"],
    )

    return df


def write_latest_reading(row):
    reading = {
        "meter_id": row.meter_id,
        "timestamp": str(row.timestamp),
        "consumption": round(float(row.consumption), 3),
        "classification": row.classification,
        "confidence_score": float(row.confidence_score),
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(reading, file, indent=2)


def stream_row(row):
    write_latest_reading(row)

    print(
        f"[STREAM] {row.timestamp} | "
        f"{row.meter_id} | "
        f"{row.consumption:.3f} kW | "
        f"{row.classification}"
    )


def main():
    df = load_data()

    normal = df[df["classification"] == "normal"]
    theft = df[df["classification"] == "theft_tampering"]
    fault = df[df["classification"] == "meter_fault"]

    if theft.empty or fault.empty:
        raise RuntimeError("Required anomaly rows were not found.")

    print("\n===== LIVE ANOMALY DEMO =====")
    print("Normal → Theft → Fault → Normal\n")

    # 10 normal readings
    for row in normal.head(10).itertuples(index=False):
        stream_row(row)
        time.sleep(DELAY_SECONDS)

    # Theft demonstration
    print("\n🚨 THEFT/TAMPERING EVENT\n")

    for row in theft.head(1).itertuples(index=False):
        stream_row(row)
        time.sleep(3)

    # Fault demonstration
    print("\n🚨 METER FAULT EVENT\n")

    for row in fault.head(1).itertuples(index=False):
        stream_row(row)
        time.sleep(3)

    # Return to normal
    print("\n✅ RETURNING TO NORMAL\n")

    for row in normal.iloc[10:20].itertuples(index=False):
        stream_row(row)
        time.sleep(DELAY_SECONDS)

    print("\n===== DEMO COMPLETED =====")
    print("Latest reading saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()