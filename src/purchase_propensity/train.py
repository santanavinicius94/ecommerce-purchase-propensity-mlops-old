"""Treina um baseline e regressão logística no mesmo holdout."""
import hashlib
import json
import os
from pathlib import Path

import joblib
import mlflow
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss,
    f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from purchase_propensity.data import (
    CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES, TARGET, validate,
)


def build_model(max_iter=1000, seed=42):
    preprocessing = ColumnTransformer([
        ("numeric", StandardScaler(), NUMERIC_FEATURES),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])
    return Pipeline([
        ("preprocessing", preprocessing),
        ("classifier", LogisticRegression(max_iter=max_iter, random_state=seed)),
    ])


def evaluate(target, probabilities, threshold):
    predictions = (probabilities >= threshold).astype(int)
    return {
        "roc_auc": float(roc_auc_score(target, probabilities)),
        "average_precision": float(average_precision_score(target, probabilities)),
        "brier_score": float(brier_score_loss(target, probabilities)),
        "precision": float(precision_score(target, predictions, zero_division=0)),
        "recall": float(recall_score(target, predictions, zero_division=0)),
        "f1": float(f1_score(target, predictions, zero_division=0)),
        "accuracy": float(accuracy_score(target, predictions)),
    }


def train():
    params = yaml.safe_load(Path("params.yaml").read_text())["train"]
    if not 0.1 <= params["test_size"] <= 0.5:
        raise ValueError("test_size deve estar entre 0.1 e 0.5.")
    if not 0 < params["threshold"] < 1:
        raise ValueError("threshold deve estar entre 0 e 1.")
    source = Path("data/processed/sessions.csv")
    frame = validate(pd.read_csv(source))
    x_train, x_test, y_train, y_test = train_test_split(
        frame[FEATURES], frame[TARGET], test_size=params["test_size"],
        random_state=params["seed"], stratify=frame[TARGET],
    )
    model = build_model(params["max_iter"], params["seed"])
    model.fit(x_train, y_train)
    baseline = DummyClassifier(strategy="prior").fit(x_train, y_train)
    metrics = evaluate(y_test, model.predict_proba(x_test)[:, 1], params["threshold"])
    metrics.update({f"baseline_{key}": value for key, value in evaluate(
        y_test, baseline.predict_proba(x_test)[:, 1], params["threshold"],
    ).items()})
    metrics["test_purchase_rate"] = float(y_test.mean())
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", Path("mlruns").resolve().as_uri()))
    mlflow.set_experiment("ecommerce-purchase-propensity")
    with mlflow.start_run():
        mlflow.log_params({**params, "train_rows": len(x_train), "test_rows": len(x_test)})
        mlflow.set_tags({
            "dataset_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "estimator": "LogisticRegression", "split": "stratified_holdout",
        })
        mlflow.log_metrics(metrics)
        Path("models").mkdir(exist_ok=True)
        Path("reports").mkdir(exist_ok=True)
        joblib.dump(model, "models/purchase_propensity.joblib")
        Path("reports/metrics.json").write_text(json.dumps(metrics, indent=2))
        mlflow.log_artifact("models/purchase_propensity.joblib", artifact_path="model")
        mlflow.log_artifact("reports/metrics.json")
        mlflow.log_artifact("params.yaml")
    return metrics


if __name__ == "__main__":
    print(json.dumps(train(), indent=2))
