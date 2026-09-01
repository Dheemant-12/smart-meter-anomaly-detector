from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest


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
    / "isolation_forest_results.csv"
)


CONTAMINATION = 0.01


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


def detect_anomalies(df):
    print("Running Isolation Forest...")

    df["isolation_anomaly"] = False
    df["isolation_score"] = 0.0

    for meter_id, meter_data in df.groupby("meter_id"):

        features = meter_data[
            ["consumption"]
        ]

        model = IsolationForest(
            contamination=CONTAMINATION,
            random_state=42
        )

        predictions = model.fit_predict(features)

        scores = model.decision_function(
            features
        )

        indices = meter_data.index

        df.loc[
            indices,
            "isolation_anomaly"
        ] = predictions == -1

        df.loc[
            indices,
            "isolation_score"
        ] = scores

    return df


def save_results(df):
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Results saved to: {OUTPUT_FILE}"
    )


def show_results(df):
    print("\nDetection results:")

    print(
        df["isolation_anomaly"]
        .value_counts()
    )

    print("\nAnomalies by meter:")

    anomalies = df[
        df["isolation_anomaly"]
    ]

    print(
        anomalies
        .groupby("meter_id")
        .size()
    )


def main():
    df = load_data()

    df = detect_anomalies(df)

    save_results(df)

    show_results(df)


if __name__ == "__main__":
    main()