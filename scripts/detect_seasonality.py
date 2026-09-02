from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose


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
    / "seasonal_results.csv"
)

# The dataset is minute-level.
# 60 readings = approximately one hour.
SEASONAL_PERIOD = 60

RESIDUAL_THRESHOLD = 3.0


def load_data():
    print("Loading meter data...")

    df = pd.read_csv(INPUT_FILE)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    df = df.sort_values(
        ["meter_id", "timestamp"]
    )

    return df


def detect_seasonal_anomalies(df):
    print("Running seasonal decomposition...")

    df["trend"] = np.nan
    df["seasonal"] = np.nan
    df["residual"] = np.nan
    df["seasonal_anomaly"] = False

    for meter_id, meter_data in df.groupby("meter_id"):

        meter_data = meter_data.sort_values("timestamp")

        series = meter_data.set_index(
            "timestamp"
        )["consumption"]

        # Decomposition requires enough observations.
        if len(series) < SEASONAL_PERIOD * 2:
            continue

        try:
            result = seasonal_decompose(
                series,
                model="additive",
                period=SEASONAL_PERIOD,
                extrapolate_trend="period"
            )

            indices = meter_data.index

            df.loc[indices, "trend"] = (
                result.trend.values
            )

            df.loc[indices, "seasonal"] = (
                result.seasonal.values
            )

            df.loc[indices, "residual"] = (
                result.resid.values
            )

        except ValueError:
            print(
                f"Could not decompose {meter_id}"
            )

    # Calculate residual statistics per meter
    grouped = df.groupby("meter_id")["residual"]

    residual_mean = grouped.transform("mean")
    residual_std = grouped.transform("std")

    residual_z = (
        (df["residual"] - residual_mean)
        / residual_std.replace(0, np.nan)
    )

    df["residual_z_score"] = residual_z.fillna(0)

    df["seasonal_anomaly"] = (
        df["residual_z_score"].abs()
        > RESIDUAL_THRESHOLD
    )

    return df


def save_results(df):
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nResults saved to: {OUTPUT_FILE}"
    )


def show_results(df):
    print("\nSeasonal detector results:")

    print(
        df["seasonal_anomaly"]
        .value_counts()
    )

    print("\nAnomalies by meter:")

    anomalies = df[
        df["seasonal_anomaly"]
    ]

    print(
        anomalies
        .groupby("meter_id")
        .size()
    )


def main():
    df = load_data()

    df = detect_seasonal_anomalies(df)

    save_results(df)

    show_results(df)


if __name__ == "__main__":
    main()
