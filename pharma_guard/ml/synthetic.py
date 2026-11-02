import numpy as np

from pharma_guard.schemas import Telemetry


def generate_dataset(
    n_normal: int = 1000,
    n_anomalies: int = 200,
    seed: int = 42,
):
    rng = np.random.default_rng(seed)

    records = []
    labels = []

    for index in range(n_normal):
        records.append(Telemetry(
            device_id="SIM-001",
            shipment_id=f"NORMAL-{index}",
            temperature_c=float(rng.normal(5.0, 0.6)),
            humidity_rh=float(rng.normal(45.0, 8.0)),
            light_lux=float(max(0, rng.normal(5.0, 3.0))),
            accel_x_g=float(rng.normal(0, 0.08)),
            accel_y_g=float(rng.normal(0, 0.08)),
            accel_z_g=float(rng.normal(1, 0.08)),
            source="synthetic",
        ))
        labels.append(0)

    for index in range(n_anomalies):
        anomaly_type = index % 4

        temperature = float(rng.normal(5.0, 0.6))
        humidity = float(rng.normal(45.0, 8.0))
        light = float(max(0, rng.normal(5.0, 3.0)))
        ax = float(rng.normal(0, 0.08))
        ay = float(rng.normal(0, 0.08))
        az = float(rng.normal(1, 0.08))

        if anomaly_type == 0:
            temperature = float(rng.choice([
                rng.normal(-2, 0.5),
                rng.normal(12, 1.0),
            ]))
        elif anomaly_type == 1:
            humidity = float(rng.normal(95, 2))
        elif anomaly_type == 2:
            light = float(rng.normal(500, 50))
        else:
            ax = float(rng.normal(4, 0.3))
            ay = float(rng.normal(3, 0.3))
            az = float(rng.normal(2, 0.3))

        records.append(Telemetry(
            device_id="SIM-001",
            shipment_id=f"ANOMALY-{index}",
            temperature_c=temperature,
            humidity_rh=humidity,
            light_lux=light,
            accel_x_g=ax,
            accel_y_g=ay,
            accel_z_g=az,
            source="synthetic",
        ))
        labels.append(1)

    return records, np.array(labels)
