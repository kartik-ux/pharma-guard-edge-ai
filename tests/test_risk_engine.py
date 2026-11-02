from pharma_guard.schemas import Telemetry
from pharma_guard.services.risk_engine import RiskEngine


def test_normal_temperature_is_low_risk():
    telemetry = Telemetry(
        device_id="TELIT-001",
        shipment_id="SHIP-001",
        temperature_c=5.0,
        humidity_rh=50,
        light_lux=10,
    )

    result = RiskEngine().assess(telemetry)

    assert result.risk_level == "LOW"
    assert result.risk_score == 0


def test_high_temperature_is_high_risk():
    telemetry = Telemetry(
        device_id="TELIT-001",
        shipment_id="SHIP-002",
        temperature_c=12.0,
    )

    result = RiskEngine().assess(telemetry)

    assert result.risk_level == "MEDIUM"
    assert result.risk_score == 50
    assert any("above demonstration limit" in reason for reason in result.reasons)


def test_missing_temperature_is_flagged():
    telemetry = Telemetry(
        device_id="TELIT-001",
        shipment_id="SHIP-003",
    )

    result = RiskEngine().assess(telemetry)

    assert result.risk_score == 15
    assert "Temperature measurement unavailable" in result.reasons


def test_invalid_temperature_is_rejected():
    try:
        Telemetry(
            device_id="TELIT-001",
            shipment_id="SHIP-004",
            temperature_c=150,
        )
        assert False, "Expected validation error"
    except ValueError:
        pass
