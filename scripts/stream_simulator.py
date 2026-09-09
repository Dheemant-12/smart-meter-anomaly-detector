from pathlib import Path
import json
import time
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "api_dataset.csv"
LATEST_FILE = BASE_DIR / "data" / "processed" / "latest_reading.json"
HISTORY_FILE = BASE_DIR / "data" / "processed" / "stream_history.json"

DELAY_SECONDS = 1


def load_data():
    print("Loading API dataset...")

    return pd.read_csv(
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


def create_reading(row):
    return {
        "meter_id": row.meter_id,
        "timestamp": str(row.timestamp),
        "consumption": round(float(row.consumption), 3),
        "classification": row.classification,
        "confidence_score": float(row.confidence_score),
    }


def save_reading(reading, history):
    with open(LATEST_FILE, "w", encoding="utf-8") as file:
        json.dump(reading, file, indent=2)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)


def main():
    df = load_data()

    normal = df[df["classification"] == "normal"]
    theft = df[df["classification"] == "theft_tampering"]
    fault = df[df["classification"] == "meter_fault"]

    if theft.empty or fault.empty:
        raise RuntimeError("Required anomaly rows were not found.")

    print("\n===== LIVE STREAM WITH HISTORY =====\n")

    history = []

    # Normal readings
    for row in normal.head(10).itertuples(index=False):
        reading = create_reading(row)
        history.append(reading)
        save_reading(reading, history)

        print(
            f"[STREAM] {reading['meter_id']} | "
            f"{reading['consumption']} kW | "
            f"{reading['classification']}"
        )

        time.sleep(DELAY_SECONDS)

    # Theft
    print("\n🚨 THEFT/TAMPERING EVENT\n")

    row = theft.head(1).iloc[0]
    reading = create_reading(row)
    history.append(reading)
    save_reading(reading, history)

    print(
        f"[STREAM] {reading['meter_id']} | "
        f"{reading['consumption']} kW | "
        f"{reading['classification']}"
    )

    time.sleep(3)

    # Fault
    print("\n🚨 METER FAULT EVENT\n")

    row = fault.head(1).iloc[0]
    reading = create_reading(row)
    history.append(reading)
    save_reading(reading, history)

    print(
        f"[STREAM] {reading['meter_id']} | "
        f"{reading['consumption']} kW | "
        f"{reading['classification']}"
    )

    time.sleep(3)

    # Normal again
    print("\n✅ RETURNING TO NORMAL\n")

    for row in normal.iloc[10:20].itertuples(index=False):
        reading = create_reading(row)
        history.append(reading)
        save_reading(reading, history)

        print(
            f"[STREAM] {reading['meter_id']} | "
            f"{reading['consumption']} kW | "
            f"{reading['classification']}"
        )

        time.sleep(DELAY_SECONDS)

    print("\n===== STREAM COMPLETED =====")
    print(f"History entries: {len(history)}")
    print(f"Saved to: {HISTORY_FILE}")


if __name__ == "__main__":
    main()