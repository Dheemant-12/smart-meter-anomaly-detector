from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "classified_results.csv"
)

df = None


def load_data():
    global df

    if df is None:
        if not DATA_FILE.exists():
            raise FileNotFoundError(
                f"Data file not found: {DATA_FILE}"
            )

        df = pd.read_csv(DATA_FILE)

    return df


@router.get("/meters")
def get_meters():
    data = load_data()

    meters = sorted(
        data["meter_id"].unique().tolist()
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
        ].to_dict(orient="records"),
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
        ].to_dict(orient="records"),
    }