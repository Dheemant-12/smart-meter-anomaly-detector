from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "ensemble_results.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "confidence_results.csv"
)


def load_data():
    print("Loading ensemble results...")

    df = pd.read_csv(INPUT_FILE)

    required = [
        "meter_id",
        "timestamp",
        "consumption",
        "detector_count",
        "ensemble_status",
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return df


def calculate_confidence(df):
    print("Calculating confidence scores...")

    # 3 detectors are currently used:
    # Z-score, Isolation Forest, Seasonal
    df["confidence_score"] = (
        df["detector_count"] / 3 * 100
    ).round(2)

    return df


def save_results(df):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nResults saved:")
    print(OUTPUT_FILE)


def show_results(df):
    print("\n===== DAY 9 RESULTS =====")

    print("\nConfidence distribution:")
    print(
        df["confidence_score"]
        .value_counts()
        .sort_index()
    )

    print("\nAverage confidence by status:")
    print(
        df.groupby("ensemble_status")["confidence_score"]
        .mean()
        .round(2)
    )

    print("\nSample:")
    print(
        df[
            [
                "meter_id",
                "timestamp",
                "detector_count",
                "ensemble_status",
                "confidence_score",
            ]
        ].head(10)
    )


def main():
    df = load_data()
    df = calculate_confidence(df)
    save_results(df)
    show_results(df)

    print("\nDay 9 completed successfully.")


if __name__ == "__main__":
    main()