from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from pharma_guard.schemas import Telemetry
from pharma_guard.services.database import (
    SessionLocal,
    TelemetryRecord,
    initialise_database,
)
from pharma_guard.services.risk_engine import RiskEngine
from pharma_guard.ml.anomaly_detector import AnomalyDetector


app = FastAPI(
    title="PHARMA-GUARD Edge AI",
    description=(
        "Pharmaceutical cold-chain monitoring and "
        "anomaly detection prototype."
    ),
    version="0.1.0",
)

risk_engine = RiskEngine()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "isolation_forest.joblib"

anomaly_detector = AnomalyDetector()
model_available = False


@app.on_event("startup")
def startup():
    global model_available

    initialise_database()

    if MODEL_PATH.exists():
        try:
            anomaly_detector.load(MODEL_PATH)
            model_available = True
            print("PHARMA-GUARD AI model loaded successfully.")
        except Exception as exc:
            print(f"Could not load AI model: {exc}")
            model_available = False
    else:
        print("AI model not found. Running rules-only mode.")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "project": "PHARMA-GUARD",
        "status": "running",
        "model_available": model_available,
        "documentation": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "ai_model_loaded": model_available,
        "database": "sqlite",
    }


@app.post("/telemetry")
def receive_telemetry(
    telemetry: Telemetry,
    db: Session = Depends(get_db),
):
    # 1. Run explainable risk assessment.
    assessment = risk_engine.assess(telemetry)

    risk_score = assessment.risk_score
    reasons = list(assessment.reasons)

    anomaly_detected = False
    anomaly_score = 0.0

    # 2. Run AI anomaly detection when the model is available.
    if model_available:
        try:
            prediction = anomaly_detector.predict([telemetry])[0]

            anomaly_detected = prediction["is_anomaly"]
            anomaly_score = prediction["decision_score"]

            if anomaly_detected:
                risk_score = min(100.0, risk_score + 20.0)
                reasons.append("Isolation Forest detected an anomaly")

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"AI inference failed: {exc}",
            )

    # 3. Combine the rule-based and AI assessments.
    if risk_score >= 60:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # 4. Persist the telemetry and assessment.
    record = TelemetryRecord(
        device_id=telemetry.device_id,
        shipment_id=telemetry.shipment_id,
        timestamp=telemetry.timestamp,
        telemetry=telemetry.model_dump(mode="json"),
        risk_score=risk_score,
        risk_level=risk_level,
        anomaly_detected=anomaly_detected,
        anomaly_score=anomaly_score,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "record_id": record.id,
        "shipment_id": telemetry.shipment_id,
        "device_id": telemetry.device_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "anomaly_detected": anomaly_detected,
        "anomaly_score": anomaly_score,
        "reasons": reasons,
        "model_available": model_available,
        "message": "Telemetry successfully processed",
    }


@app.get("/shipments/{shipment_id}")
def get_shipment(
    shipment_id: str,
    db: Session = Depends(get_db),
):
    records = (
        db.query(TelemetryRecord)
        .filter(TelemetryRecord.shipment_id == shipment_id)
        .order_by(TelemetryRecord.id.desc())
        .all()
    )

    if not records:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found",
        )

    return {
        "shipment_id": shipment_id,
        "total_records": len(records),
        "records": [
            {
                "record_id": record.id,
                "timestamp": record.timestamp,
                "risk_score": record.risk_score,
                "risk_level": record.risk_level,
                "anomaly_detected": record.anomaly_detected,
                "telemetry": record.telemetry,
            }
            for record in records
        ],
    }


@app.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    records = db.query(TelemetryRecord).all()

    return {
        "total_readings": len(records),
        "high_risk_readings": sum(
            record.risk_level == "HIGH" for record in records
        ),
        "medium_risk_readings": sum(
            record.risk_level == "MEDIUM" for record in records
        ),
        "low_risk_readings": sum(
            record.risk_level == "LOW" for record in records
        ),
        "anomalies_detected": sum(
            record.anomaly_detected for record in records
        ),
    }


@app.get("/readings/latest")
def latest_readings(db: Session = Depends(get_db)):
    records = (
        db.query(TelemetryRecord)
        .order_by(TelemetryRecord.id.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": record.id,
            "device_id": record.device_id,
            "shipment_id": record.shipment_id,
            "timestamp": record.timestamp.isoformat()
            if record.timestamp else None,
            "temperature_c": record.telemetry.get("temperature_c"),
            "humidity_rh": record.telemetry.get("humidity_rh"),
            "light_lux": record.telemetry.get("light_lux"),
            "risk_score": record.risk_score,
            "risk_level": record.risk_level,
            "anomaly_detected": record.anomaly_detected,
        }
        for record in records
    ]


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    from fastapi.responses import FileResponse

    dashboard_file = (
        Path(__file__).resolve().parent / "static" / "dashboard.html"
    )
    return FileResponse(dashboard_file)
