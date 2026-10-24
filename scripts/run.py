"""Executa preparação e treino com o CSV fornecido pelo usuário."""
import subprocess
import sys

for module in ("purchase_propensity.data", "purchase_propensity.train"):
    subprocess.run([sys.executable, "-m", module], check=True)
