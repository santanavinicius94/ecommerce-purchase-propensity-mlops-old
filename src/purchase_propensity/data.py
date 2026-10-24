"""Contrato de entrada e preparação dos dados de sessões."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

NUMERIC_FEATURES = ["pages_viewed", "time_on_site_seconds", "cart_items"]
CATEGORICAL_FEATURES = ["traffic_source", "device_type"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "purchased"


def validate(frame: pd.DataFrame) -> pd.DataFrame:
    required = ["session_id", *FEATURES, TARGET]
    missing = set(required) - set(frame.columns)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}")
    frame = frame[required].copy()
    if frame.empty or frame.isna().any().any():
        raise ValueError("O dataset deve conter linhas sem valores ausentes.")
    if frame["session_id"].duplicated().any():
        raise ValueError("session_id deve ser único.")
    if frame["session_id"].astype(str).str.strip().eq("").any():
        raise ValueError("session_id não pode ser vazio.")
    values = frame[NUMERIC_FEATURES].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(values.to_numpy(dtype=float)).all() or (values < 0).any().any():
        raise ValueError("Features numéricas devem ser finitas e não negativas.")
    for column in ["pages_viewed", "cart_items"]:
        if (values[column] % 1 != 0).any():
            raise ValueError(f"{column} deve conter contagens inteiras.")
    frame[NUMERIC_FEATURES] = values
    for column in CATEGORICAL_FEATURES:
        if frame[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"{column} não pode ser vazio.")
        frame[column] = frame[column].astype(str)
    if not frame[TARGET].isin([0, 1]).all() or frame[TARGET].nunique() != 2:
        raise ValueError("purchased deve conter as duas classes 0 e 1.")
    if frame[TARGET].value_counts().min() < 10:
        raise ValueError("São necessárias pelo menos 10 sessões por classe.")
    frame[TARGET] = frame[TARGET].astype(int)
    return frame


def prepare(source="data/raw/sessions.csv", output="data/processed/sessions.csv"):
    frame = validate(pd.read_csv(source))
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="data/raw/sessions.csv")
    parser.add_argument("--output", default="data/processed/sessions.csv")
    args = parser.parse_args()
    prepare(args.source, args.output)
