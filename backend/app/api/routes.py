from pathlib import Path
import json

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

LATEST_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "latest_reading.json"
)

HISTORY_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "stream_history.json"
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
        data["meter_id"].unique().tolist()
    )

    return {
        "count": len(meters),
        "meters": meters,
    }


@router.get("/summary")
def get_summary():
    data = load_data()

    anomalies = data[
        data["classification"] != "normal"
    ]

    theft_count = int(
        (
            data["classification"]
            == "theft_tampering"
        ).sum()
    )

    fault_count = int(
        (
            data["classification"]
            == "meter_fault"
        ).sum()
    )

    return {
        "total_meters": int(
            data["meter_id"].nunique()
        ),
        "total_readings": len(data),
        "total_anomalies": len(anomalies),
        "theft_tampering": theft_count,
        "meter_faults": fault_count,
    }


@router.get("/anomalies")
def get_anomalies():
    data = load_data()

    anomalies = data[
        data["classification"] != "normal"
    ]

    anomalies = anomalies.sort_values(
        "timestamp",
        ascending=False,
    )

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
    ].sort_values(
        "timestamp",
        ascending=False,
    )

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


@router.get("/stream/latest")
def get_latest_reading():
    if not LATEST_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="No stream reading available",
        )

    with open(
        LATEST_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        reading = json.load(file)

    return reading


@router.get("/stream/history")
def get_stream_history():
    if not HISTORY_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="No stream history available",
        )

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        history = json.load(file)

    return {
        "count": len(history),
        "history": history,
    }


@router.get("/stream/stats")
def get_stream_stats():
    if not HISTORY_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="No stream history available",
        )

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        history = json.load(file)

    normal_count = sum(
        reading["classification"] == "normal"
        for reading in history
    )

    theft_count = sum(
        reading["classification"]
        == "theft_tampering"
        for reading in history
    )

    fault_count = sum(
        reading["classification"]
        == "meter_fault"
        for reading in history
    )

    return {
        "total_readings": len(history),
        "normal": normal_count,
        "anomalies": theft_count + fault_count,
        "theft_tampering": theft_count,
        "meter_faults": fault_count,
    }