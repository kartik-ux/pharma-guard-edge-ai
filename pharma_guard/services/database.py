from pathlib import Path

from sqlalchemy import create_engine, String, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "pharma_guard.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    device_id: Mapped[str] = mapped_column(String(100), index=True)
    shipment_id: Mapped[str] = mapped_column(String(100), index=True)

    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    telemetry: Mapped[dict] = mapped_column(JSON)

    risk_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(20))

    anomaly_detected: Mapped[bool] = mapped_column(Boolean)
    anomaly_score: Mapped[float] = mapped_column(Float)


def initialise_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
