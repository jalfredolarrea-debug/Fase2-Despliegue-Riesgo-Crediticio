FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY artifacts/modelo_riesgo.joblib artifacts/
COPY artifacts/metadata.json artifacts/
COPY frontend/form_schema.json frontend/
COPY src/api.py src/

RUN useradd --uid 10001 --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
