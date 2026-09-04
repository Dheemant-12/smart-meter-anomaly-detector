from pathlib import Path

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "classified_results.csv"
)


def load_data():
    print("Loading classified results...")

    df = pd.read_csv(INPUT_FILE)

    required = [
        "anomaly_type",
        "classification",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return df


def create_labels(df):
    print("Preparing evaluation labels...")

    # Ground truth:
    # normal -> normal
    # theft -> anomaly
    # fault -> anomaly
    df["actual_anomaly"] = (
        df["anomaly_type"] != "normal"
    )

    # Detector result:
    df["predicted_anomaly"] = (
        df["classification"] != "normal"
    )

    return df


def show_confusion_matrix(df):
    actual = df["actual_anomaly"]
    predicted = df["predicted_anomaly"]

    matrix = confusion_matrix(
        actual,
        predicted,
        labels=[False, True],
    )

    tn, fp, fn, tp = matrix.ravel()

    print("\n===== CONFUSION MATRIX =====")
    print(f"True Negatives : {tn:,}")
    print(f"False Positives: {fp:,}")
    print(f"False Negatives: {fn:,}")
    print(f"True Positives : {tp:,}")


def show_metrics(df):
    print("\n===== DETECTION METRICS =====")

    print(
        classification_report(
            df["actual_anomaly"],
            df["predicted_anomaly"],
            target_names=["normal", "anomaly"],
            zero_division=0,
        )
    )


def show_ground_truth(df):
    print("\n===== GROUND TRUTH =====")

    print(
        df["anomaly_type"]
        .value_counts()
    )

    print("\n===== PREDICTIONS =====")

    print(
        df["classification"]
        .value_counts()
    )


def main():
    df = load_data()

    df = create_labels(df)

    show_ground_truth(df)

    show_confusion_matrix(df)

    show_metrics(df)

    print("\nDay 11 completed successfully.")


if __name__ == "__main__":
    main()