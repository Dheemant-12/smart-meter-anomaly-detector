from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "meter_data_with_anomalies.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "zscore_results.csv"
)


WINDOW_SIZE = 60
Z_THRESHOLD = 3.0


def load_data():
    print("Loading meter data...")

    df = pd.read_csv(INPUT_FILE)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.sort_values(
        ["meter_id", "timestamp"]
    )

    return df


def calculate_zscore(df):
    print("Calculating rolling z-scores...")

    grouped = df.groupby("meter_id")["consumption"]

    rolling_mean = grouped.transform(
        lambda x: x.rolling(
            WINDOW_SIZE,
            min_periods=10
        ).mean()
    )

    rolling_std = grouped.transform(
        lambda x: x.rolling(
            WINDOW_SIZE,
            min_periods=10
        ).std()
    )

    df["rolling_mean"] = rolling_mean
    df["rolling_std"] = rolling_std

    df["z_score"] = (
        (df["consumption"] - df["rolling_mean"])
        / df["rolling_std"].replace(0, np.nan)
    )

    df["z_score"] = df["z_score"].fillna(0)

    df["zscore_anomaly"] = (
        df["z_score"].abs() > Z_THRESHOLD
    )

    return df


def save_results(df):
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Results saved to: {OUTPUT_FILE}")


def show_results(df):
    print("\nDetector results:")
    print(
        df["zscore_anomaly"]
        .value_counts()
    )

    print("\nDetected anomalies by meter:")

    anomalies = df[df["zscore_anomaly"]]

    print(
        anomalies
        .groupby("meter_id")
        .size()
    )


def main():
    df = load_data()

    df = calculate_zscore(df)

    save_results(df)

    show_results(df)


if __name__ == "__main__":
    main()