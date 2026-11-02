from pharma_guard.schemas import Telemetry, RiskAssessment


class RiskEngine:
    """
    Explainable rule-based risk engine.

    Demonstration profile only:
    Temperature range: 2 to 8 degrees Celsius.
    Replace these limits with approved product-specific limits.
    """

    def __init__(
        self,
        min_temperature: float = 2.0,
        max_temperature: float = 8.0,
    ):
        if min_temperature >= max_temperature:
            raise ValueError("Minimum temperature must be below maximum")

        self.min_temperature = min_temperature
        self.max_temperature = max_temperature

    def assess(self, telemetry: Telemetry) -> RiskAssessment:
        score = 0.0
        reasons = []

        temperature = telemetry.temperature_c

        if temperature is None:
            reasons.append("Temperature measurement unavailable")
            score += 15

        elif temperature < self.min_temperature:
            score += 50
            reasons.append(
                f"Temperature below demonstration limit: {temperature} °C"
            )

        elif temperature > self.max_temperature:
            score += 50
            reasons.append(
                f"Temperature above demonstration limit: {temperature} °C"
            )

        if telemetry.humidity_rh is not None:
            if telemetry.humidity_rh > 80:
                score += 15
                reasons.append("High humidity detected")

        if telemetry.light_lux is not None:
            if telemetry.light_lux > 100:
                score += 15
                reasons.append("Possible light exposure detected")

        acceleration = [
            telemetry.accel_x_g,
            telemetry.accel_y_g,
            telemetry.accel_z_g,
        ]

        if all(value is not None for value in acceleration):
            magnitude = sum(value ** 2 for value in acceleration) ** 0.5

            # Demonstration threshold, not a validated shock specification.
            if magnitude > 3.0:
                score += 20
                reasons.append("Potential high-magnitude movement detected")

        score = min(score, 100)

        if score >= 60:
            level = "HIGH"
        elif score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"

        if not reasons:
            reasons.append("No configured risk conditions detected")

        return RiskAssessment(
            shipment_id=telemetry.shipment_id,
            risk_score=score,
            risk_level=level,
            reasons=reasons,
        )
