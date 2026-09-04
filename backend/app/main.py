from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Smart Meter Anomaly Detector",
    description="Real-time smart meter theft and fault detection system",
    version="0.2.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Smart Meter Anomaly Detector API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }