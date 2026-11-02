import pytest

from pharma_guard.ml.anomaly_detector import AnomalyDetector
from pharma_guard.ml.synthetic import generate_dataset


def test_model_requires_training_before_prediction():
    detector = AnomalyDetector()

    records, _ = generate_dataset(
        n_normal=2,
        n_anomalies=0,
    )

    with pytest.raises(RuntimeError):
        detector.predict(records)


def test_model_trains_and_predicts():
    records, _ = generate_dataset(
        n_normal=200,
        n_anomalies=0,
    )

    detector = AnomalyDetector()
    detector.fit(records)

    predictions = detector.predict(records[:10])

    assert len(predictions) == 10
    assert all(
        result["label"] in ["NORMAL", "ANOMALY"]
        for result in predictions
    )


def test_model_can_be_saved_and_loaded(tmp_path):
    records, _ = generate_dataset(
        n_normal=200,
        n_anomalies=0,
    )

    detector = AnomalyDetector()
    detector.fit(records)

    model_path = tmp_path / "model.joblib"
    detector.save(model_path)

    restored = AnomalyDetector()
    restored.load(model_path)

    predictions = restored.predict(records[:5])

    assert len(predictions) == 5
