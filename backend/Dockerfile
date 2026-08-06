# Build from the repository root so this can see the sibling modules it
# imports (business_metrics.py, ai_insights.py, config.py, utils/, data/):
#   docker build -f backend/Dockerfile -t business-reports-api .
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
