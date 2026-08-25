from fastapi import FastAPI

app = FastAPI(
    title="Smart Meter Anomaly Detector",
    description="Real-time smart meter theft and fault detection system",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Smart Meter Anomaly Detector API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }