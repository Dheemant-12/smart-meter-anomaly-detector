from pathlib import Path
import time

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "api_dataset.csv"
)

# Keep the demo tiny and fast.
READINGS_PER_METER = 20
DELAY_SECONDS = 0.05


def load_data():
    print("Loading API dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        parse_dates=["timestamp"],
    )

    df = df.sort_values(
        ["timestamp", "meter_id"]
    )

    return df


def stream_data(df):
    print("\n===== LIVE METER STREAM =====")
    print("Starting stream...\n")

    count = 0

    for _, row in df.iterrows():
        print(
            f"[STREAM] "
            f"{row['timestamp']} | "
            f"{row['meter_id']} | "
            f"{row['consumption']:.3f} kW | "
            f"{row['classification']}"
        )

        count += 1

        if count >= READINGS_PER_METER * 10:
            break

        time.sleep(DELAY_SECONDS)

    print(
        f"\nStreamed {count} readings successfully."
    )


def main():
    df = load_data()
    stream_data(df)

    print("\nDay 18 streaming simulation completed.")


if __name__ == "__main__":
    main()