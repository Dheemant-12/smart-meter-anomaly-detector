from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "classified_results.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "api_dataset.csv"
)

NORMAL_ROWS_PER_METER = 2000
CHUNK_SIZE = 200_000


def create_dataset():
    print("Creating lightweight API dataset...")
    print("Reading large dataset in chunks...")

    normal_samples = []
    anomalies = []
    normal_counts = {}

    required_columns = [
        "meter_id",
        "timestamp",
        "consumption",
        "classification",
        "confidence_score",
    ]

    for chunk_number, chunk in enumerate(
        pd.read_csv(
            INPUT_FILE,
            usecols=required_columns,
            chunksize=CHUNK_SIZE,
        ),
        start=1,
    ):
        print(f"Processing chunk {chunk_number}...")

        anomaly_rows = chunk[
            chunk["classification"] != "normal"
        ]

        if not anomaly_rows.empty:
            anomalies.append(anomaly_rows)

        normal_rows = chunk[
            chunk["classification"] == "normal"
        ]

        if not normal_rows.empty:
            for meter_id, meter_data in normal_rows.groupby(
                "meter_id"
            ):
                current_count = normal_counts.get(
                    meter_id,
                    0,
                )

                remaining = (
                    NORMAL_ROWS_PER_METER
                    - current_count
                )

                if remaining <= 0:
                    continue

                sample = meter_data.head(remaining)

                normal_samples.append(sample)

                normal_counts[meter_id] = (
                    current_count
                    + len(sample)
                )

    print("\nCombining data...")

    normal_df = pd.concat(
        normal_samples,
        ignore_index=True,
    )

    anomaly_df = pd.concat(
        anomalies,
        ignore_index=True,
    )

    result = pd.concat(
        [normal_df, anomaly_df],
        ignore_index=True,
    )

    result = result.drop_duplicates(
        subset=[
            "meter_id",
            "timestamp",
        ]
    )

    result["timestamp"] = pd.to_datetime(
        result["timestamp"]
    )

    result = result.sort_values(
        ["meter_id", "timestamp"]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\n===== API DATASET CREATED =====")
    print(f"Rows: {len(result):,}")
    print(f"Meters: {result['meter_id'].nunique()}")

    print("\nClassification counts:")
    print(
        result["classification"]
        .value_counts()
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)


def main():
    create_dataset()

    print("\nDay 15 dataset preparation completed.")


if __name__ == "__main__":
    main()