from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class Telemetry(BaseModel):
    """Canonical telemetry format used internally by PHARMA-GUARD."""

    model_config = ConfigDict(extra="forbid")

    device_id: str = Field(min_length=1, max_length=100)
    shipment_id: str = Field(min_length=1, max_length=100)

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    temperature_c: Optional[float] = Field(default=None, ge=-100, le=100)
    humidity_rh: Optional[float] = Field(default=None, ge=0, le=100)
    light_lux: Optional[float] = Field(default=None, ge=0, le=200000)

    accel_x_g: Optional[float] = Field(default=None, ge=-100, le=100)
    accel_y_g: Optional[float] = Field(default=None, ge=-100, le=100)
    accel_z_g: Optional[float] = Field(default=None, ge=-100, le=100)

    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    source: str = Field(default="unknown", max_length=100)

    @field_validator("timestamp")
    @classmethod
    def normalise_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class RiskAssessment(BaseModel):
    shipment_id: str
    risk_score: float = Field(ge=0, le=100)
    risk_level: str
    reasons: list[str]
    assessed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
