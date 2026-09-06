from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "api_dataset.csv"
)

_df = None


def load_data():
    global _df

    if _df is None:
        if not DATA_FILE.exists():
            raise FileNotFoundError(
                f"API dataset not found: {DATA_FILE}"
            )

        print("Loading lightweight API dataset...")

        _df = pd.read_csv(
            DATA_FILE,
            parse_dates=["timestamp"],
        )

        print(f"Loaded {_df.shape[0]:,} rows.")

    return _df


@router.get("/meters")
def get_meters():
    data = load_data()

    meters = sorted(
        data["meter_id"]
        .unique()
        .tolist()
    )

    return {
        "count": len(meters),
        "meters": meters,
    }


@router.get("/anomalies")
def get_anomalies():
    data = load_data()

    anomalies = data[
        data["classification"] != "normal"
    ]

    return {
        "count": len(anomalies),
        "anomalies": anomalies[
            [
                "meter_id",
                "timestamp",
                "consumption",
                "classification",
                "confidence_score",
            ]
        ].to_dict(
            orient="records"
        ),
    }


@router.get("/meters/{meter_id}")
def get_meter(meter_id: str):
    data = load_data()

    meter_data = data[
        data["meter_id"] == meter_id
    ]

    if meter_data.empty:
        raise HTTPException(
            status_code=404,
            detail="Meter not found",
        )

    anomalies = meter_data[
        meter_data["classification"] != "normal"
    ]

    return {
        "meter_id": meter_id,
        "total_readings": len(meter_data),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies[
            [
                "timestamp",
                "consumption",
                "classification",
                "confidence_score",
            ]
        ].to_dict(
            orient="records"
        ),
    }