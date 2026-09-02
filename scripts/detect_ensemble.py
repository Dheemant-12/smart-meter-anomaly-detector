from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "seasonal_results.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "ensemble_results.csv"
)


def load_data():
    print("Loading detector results...")

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "meter_id",
        "timestamp",
        "consumption",
        "anomaly_type",
        "seasonal_anomaly",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    return df


def create_detector_scores(df):
    print("Combining detector signals...")

    # Seasonal detector
    df["seasonal_score"] = (
        df["seasonal_anomaly"].astype(int)
    )

    # If previous detector result files exist,
    # merge their anomaly signals.
    zscore_file = (
        BASE_DIR
        / "data"
        / "processed"
        / "zscore_results.csv"
    )

    isolation_file = (
        BASE_DIR
        / "data"
        / "processed"
        / "isolation_forest_results.csv"
    )

    if zscore_file.exists():
        print("Loading Z-score detector...")
        zscore = pd.read_csv(
            zscore_file,
            usecols=[
                "meter_id",
                "timestamp",
                "zscore_anomaly",
            ],
        )

        df = df.merge(
            zscore,
            on=["meter_id", "timestamp"],
            how="left",
        )

        df["zscore_anomaly"] = (
            df["zscore_anomaly"]
            .fillna(False)
            .astype(bool)
        )
    else:
        print("Z-score results not found.")
        df["zscore_anomaly"] = False

    if isolation_file.exists():
        print("Loading Isolation Forest detector...")
        isolation = pd.read_csv(
            isolation_file,
            usecols=[
                "meter_id",
                "timestamp",
                "isolation_anomaly",
            ],
        )

        df = df.merge(
            isolation,
            on=["meter_id", "timestamp"],
            how="left",
        )

        df["isolation_anomaly"] = (
            df["isolation_anomaly"]
            .fillna(False)
            .astype(bool)
        )
    else:
        print("Isolation Forest results not found.")
        df["isolation_anomaly"] = False

    df["detector_count"] = (
        df["zscore_anomaly"].astype(int)
        + df["isolation_anomaly"].astype(int)
        + df["seasonal_anomaly"].astype(int)
    )

    return df


def classify_anomalies(df):
    print("Classifying final anomaly status...")

    df["ensemble_status"] = "normal"

    df.loc[
        df["detector_count"] == 1,
        "ensemble_status"
    ] = "suspicious"

    df.loc[
        df["detector_count"] == 2,
        "ensemble_status"
    ] = "anomaly"

    df.loc[
        df["detector_count"] >= 3,
        "ensemble_status"
    ] = "strong_anomaly"

    return df


def save_results(df):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nResults saved:")
    print(OUTPUT_FILE)


def show_results(df):
    print("\n===== DAY 8 RESULTS =====")

    print("\nDetector agreement:")
    print(
        df["detector_count"]
        .value_counts()
        .sort_index()
    )

    print("\nFinal status:")
    print(
        df["ensemble_status"]
        .value_counts()
    )

    print("\nStatus by meter:")
    print(
        df.groupby(
            ["meter_id", "ensemble_status"]
        ).size()
    )


def main():
    df = load_data()

    df = create_detector_scores(df)

    df = classify_anomalies(df)

    save_results(df)

    show_results(df)

    print("\nDay 8 completed successfully.")


if __name__ == "__main__":
    main()