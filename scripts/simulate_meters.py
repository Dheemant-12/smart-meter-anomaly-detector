from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "meter_readings.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "simulated_meters.csv"


NUMBER_OF_METERS = 10


def load_data():
    print("Loading cleaned dataset...")

    df = pd.read_csv(INPUT_FILE)

    df["datetime"] = pd.to_datetime(df["datetime"])

    return df


def create_meters(df):
    print(f"Creating {NUMBER_OF_METERS} simulated meters...")

    base_consumption = df["Global_active_power"].astype(float)

    meters = []

    rng = np.random.default_rng(42)

    for meter_number in range(1, NUMBER_OF_METERS + 1):

        meter_id = f"MTR_{meter_number:04d}"

        scale = rng.uniform(0.7, 1.4)

        noise = rng.normal(
            loc=0,
            scale=0.05,
            size=len(df)
        )

        consumption = (
            base_consumption * scale
            + noise
        )

        meter_df = pd.DataFrame(
            {
                "meter_id": meter_id,
                "timestamp": df["datetime"],
                "consumption": consumption
            }
        )

        meter_df["consumption"] = meter_df[
            "consumption"
        ].clip(lower=0)

        meters.append(meter_df)

    return pd.concat(
        meters,
        ignore_index=True
    )


def save_data(df):
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Saved simulated meters to:")
    print(OUTPUT_FILE)


def main():
    df = load_data()

    simulated_df = create_meters(df)

    save_data(simulated_df)

    print("\nSimulation completed.")
    print(f"Total rows: {len(simulated_df)}")
    print(
        f"Unique meters: "
        f"{simulated_df['meter_id'].nunique()}"
    )

    print("\nSample:")
    print(simulated_df.head())


if __name__ == "__main__":
    main()