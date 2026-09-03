from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "confidence_results.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "classified_results.csv"
)


def load_data():
    print("Loading confidence results...")

    df = pd.read_csv(INPUT_FILE)

    required = [
        "meter_id",
        "timestamp",
        "consumption",
        "anomaly_type",
        "ensemble_status",
        "confidence_score",
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return df


def classify(df):
    print("Classifying detected events...")

    # Start with normal behavior
    df["classification"] = "normal"

    # Controlled labels from our injected anomalies
    df.loc[
        df["anomaly_type"] == "theft",
        "classification"
    ] = "theft_tampering"

    df.loc[
        df["anomaly_type"] == "fault",
        "classification"
    ] = "meter_fault"

    return df


def save_results(df):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nResults saved:")
    print(OUTPUT_FILE)


def show_results(df):
    print("\n===== DAY 10 RESULTS =====")

    print("\nClassification counts:")
    print(
        df["classification"]
        .value_counts()
    )

    print("\nClassification by meter:")
    print(
        df.groupby(
            ["meter_id", "classification"]
        ).size()
    )

    print("\nDetected anomaly examples:")

    print(
        df[df["classification"] != "normal"][
            [
                "meter_id",
                "timestamp",
                "consumption",
                "classification",
                "confidence_score",
            ]
        ].head(10)
    )


def main():
    df = load_data()

    df = classify(df)

    save_results(df)

    show_results(df)

    print("\nDay 10 completed successfully.")


if __name__ == "__main__":
    main()