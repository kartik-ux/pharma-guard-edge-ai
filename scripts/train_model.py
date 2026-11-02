import json

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

from pharma_guard.ml.anomaly_detector import AnomalyDetector
from pharma_guard.ml.synthetic import generate_dataset


def main():
    training_records, _ = generate_dataset(
        n_normal=2000,
        n_anomalies=0,
        seed=42,
    )

    evaluation_records, actual_labels = generate_dataset(
        n_normal=500,
        n_anomalies=200,
        seed=99,
    )

    detector = AnomalyDetector(contamination=0.05)
    detector.fit(training_records)

    predictions = detector.predict(evaluation_records)

    predicted_labels = [
        int(result["is_anomaly"]) for result in predictions
    ]

    print("\nPHARMA-GUARD — Isolation Forest Evaluation")
    print("=" * 48)

    print("\nConfusion matrix:")
    print(confusion_matrix(actual_labels, predicted_labels))

    print("\nClassification report:")
    print(classification_report(
        actual_labels,
        predicted_labels,
        target_names=["Normal", "Anomaly"],
        zero_division=0,
    ))

    metrics = {
        "precision": precision_score(
            actual_labels, predicted_labels, zero_division=0
        ),
        "recall": recall_score(
            actual_labels, predicted_labels, zero_division=0
        ),
        "f1_score": f1_score(
            actual_labels, predicted_labels, zero_division=0
        ),
    }

    print("\nSummary metrics:")
    print(json.dumps(metrics, indent=2))

    detector.save("models/isolation_forest.joblib")
    print("\nModel saved to models/isolation_forest.joblib")


if __name__ == "__main__":
    main()
