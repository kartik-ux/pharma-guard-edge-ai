from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from pharma_guard.ml.features import extract_features
from pharma_guard.schemas import Telemetry


class AnomalyDetector:
    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
    ):
        self.contamination = contamination
        self.random_state = random_state

        self.pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", IsolationForest(
                n_estimators=200,
                contamination=contamination,
                random_state=random_state,
                n_jobs=-1,
            )),
        ])

        self.is_trained = False

    def fit(self, records: list[Telemetry]) -> None:
        if len(records) < 20:
            raise ValueError("At least 20 training records are required")

        features = extract_features(records)

        self.pipeline.fit(features)
        self.is_trained = True

    def predict(self, records: list[Telemetry]) -> list[dict]:
        if not self.is_trained:
            raise RuntimeError("Train the anomaly detector before prediction")

        if not records:
            return []

        features = extract_features(records)

        predictions = self.pipeline.predict(features)
        decision_scores = self.pipeline.decision_function(features)

        results = []

        for prediction, decision_score in zip(
            predictions, decision_scores
        ):
            results.append({
                "is_anomaly": bool(prediction == -1),
                "decision_score": float(decision_score),
                "label": "ANOMALY" if prediction == -1 else "NORMAL",
            })

        return results

    def save(self, path: str | Path) -> None:
        if not self.is_trained:
            raise RuntimeError("Cannot save an untrained model")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.pipeline, path)

    def load(self, path: str | Path) -> None:
        self.pipeline = joblib.load(path)
        self.is_trained = True
