import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

from purchase_propensity.data import FEATURES, prepare, validate
from purchase_propensity.train import train


@pytest.fixture
def sessions():
    rows = 80
    return pd.DataFrame({
        "session_id": [f"test-{i}" for i in range(rows)],
        "pages_viewed": [2, 8, 3, 12] * 20,
        "time_on_site_seconds": [30, 300, 45, 500] * 20,
        "cart_items": [0, 2, 0, 3] * 20,
        "traffic_source": ["organic", "paid"] * 40,
        "device_type": ["mobile", "desktop"] * 40,
        "purchased": [0, 1] * 40,
    })


@pytest.mark.parametrize("fault", ["missing", "duplicate", "negative", "null", "one_class", "fractional", "infinite", "blank"])
def test_invalid_input_is_rejected(sessions, fault):
    if fault == "missing":
        sessions = sessions.drop(columns="cart_items")
    elif fault == "duplicate":
        sessions.loc[1, "session_id"] = sessions.loc[0, "session_id"]
    elif fault == "negative":
        sessions.loc[0, "cart_items"] = -1
    elif fault == "null":
        sessions.loc[0, "device_type"] = None
    elif fault == "one_class":
        sessions["purchased"] = 0
    elif fault == "fractional":
        sessions["cart_items"] = 0.5
    elif fault == "infinite":
        sessions["time_on_site_seconds"] = np.inf
    elif fault == "blank":
        sessions.loc[0, "traffic_source"] = " "
    with pytest.raises(ValueError):
        validate(sessions)


def test_training_exports_probabilities_and_baseline(sessions, tmp_path, monkeypatch):
    params = Path("params.yaml").read_text()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    Path("params.yaml").write_text(params)
    sessions.to_csv("sessions.csv", index=False)
    prepare("sessions.csv")
    metrics = train()
    model = joblib.load("models/purchase_propensity.joblib")
    sample = sessions[FEATURES].iloc[:2].copy()
    sample["traffic_source"] = "unseen-source"
    probabilities = model.predict_proba(sample)[:, 1]
    assert probabilities.shape == (2,)
    assert ((probabilities >= 0) & (probabilities <= 1)).all()
    assert set(model.feature_names_in_) == set(FEATURES)
    assert "purchased" not in model.feature_names_in_
    assert "session_id" not in model.feature_names_in_
    assert "baseline_average_precision" in metrics
    assert all(np.isfinite(list(metrics.values())))
    assert json.loads(Path("reports/metrics.json").read_text()) == metrics
