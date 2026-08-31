from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "simulated_meters.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "meter_data_with_anomalies.csv"


def load_data():
    print("Loading simulated meter data...")

    df = pd.read_csv(INPUT_FILE)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["anomaly_type"] = "normal"

    return df


def inject_theft(df, meter_id, start_index, duration):
    mask = (
        (df["meter_id"] == meter_id)
        & (
            df.groupby("meter_id").cumcount()
            .between(start_index, start_index + duration - 1)
        )
    )

    df.loc[mask, "consumption"] *= 0.25
    df.loc[mask, "anomaly_type"] = "theft"

    return df


def inject_fault(df, meter_id, start_index, duration):
    mask = (
        (df["meter_id"] == meter_id)
        & (
            df.groupby("meter_id").cumcount()
            .between(start_index, start_index + duration - 1)
        )
    )

    df.loc[mask, "consumption"] = 0
    df.loc[mask, "anomaly_type"] = "fault"

    return df


def inject_spike_fault(df, meter_id, start_index, duration):
    mask = (
        (df["meter_id"] == meter_id)
        & (
            df.groupby("meter_id").cumcount()
            .between(start_index, start_index + duration - 1)
        )
    )

    df.loc[mask, "consumption"] *= 4
    df.loc[mask, "anomaly_type"] = "fault"

    return df


def main():
    df = load_data()

    # Theft / tampering
    df = inject_theft(
        df,
        meter_id="MTR_0002",
        start_index=5000,
        duration=300
    )

    # Meter stuck at zero
    df = inject_fault(
        df,
        meter_id="MTR_0004",
        start_index=8000,
        duration=200
    )

    # Abnormal meter spike
    df = inject_spike_fault(
        df,
        meter_id="MTR_0006",
        start_index=12000,
        duration=100
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nAnomaly injection completed.")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nAnomaly counts:")
    print(df["anomaly_type"].value_counts())


if __name__ == "__main__":
    main()