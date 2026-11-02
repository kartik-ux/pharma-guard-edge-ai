import numpy as np
import pandas as pd

from pharma_guard.schemas import Telemetry


FEATURE_COLUMNS = [
    "temperature_c",
    "humidity_rh",
    "light_lux",
    "acceleration_magnitude_g",
    "temperature_missing",
    "humidity_missing",
    "light_missing",
    "acceleration_missing",
]


def extract_features(records: list[Telemetry]) -> pd.DataFrame:
    rows = []

    for record in records:
        acceleration = [
            record.accel_x_g,
            record.accel_y_g,
            record.accel_z_g,
        ]

        acceleration_missing = any(value is None for value in acceleration)

        if acceleration_missing:
            magnitude = np.nan
        else:
            magnitude = float(np.linalg.norm(acceleration))

        rows.append({
            "temperature_c": record.temperature_c,
            "humidity_rh": record.humidity_rh,
            "light_lux": record.light_lux,
            "acceleration_magnitude_g": magnitude,
            "temperature_missing": int(record.temperature_c is None),
            "humidity_missing": int(record.humidity_rh is None),
            "light_missing": int(record.light_lux is None),
            "acceleration_missing": int(acceleration_missing),
        })

    return pd.DataFrame(rows, columns=FEATURE_COLUMNS)
