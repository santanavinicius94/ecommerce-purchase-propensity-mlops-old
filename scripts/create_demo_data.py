"""Gera sessões sintéticas para testes de infraestrutura; não são dados de clientes."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate(output):
    path = Path(output)
    if path.exists():
        raise FileExistsError(f"O arquivo já existe: {path}")
    rng = np.random.default_rng(42)
    rows = 200
    pages = rng.integers(1, 20, rows)
    cart = rng.integers(0, 5, rows)
    score = -3 + 0.12 * pages + 0.65 * cart
    target = rng.binomial(1, 1 / (1 + np.exp(-score)))
    frame = pd.DataFrame({
        "session_id": [f"synthetic-{i:04d}" for i in range(rows)],
        "pages_viewed": pages,
        "time_on_site_seconds": rng.integers(10, 900, rows),
        "cart_items": cart,
        "traffic_source": rng.choice(["organic", "paid", "direct"], rows),
        "device_type": rng.choice(["mobile", "desktop"], rows),
        "purchased": target,
    })
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    print(f"Dados SINTÉTICOS: {path} ({rows} linhas). Não usar como evidência de performance.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output")
    generate(parser.parse_args().output)
