FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir --no-deps .
COPY params.yaml ./
COPY scripts ./scripts
RUN useradd --create-home runner && chown -R runner:runner /app
USER runner
CMD ["python", "scripts/run.py"]
