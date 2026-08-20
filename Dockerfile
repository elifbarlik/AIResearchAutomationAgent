FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# ${PORT:-8000}: Railway injects PORT at runtime; the fallback keeps plain
# `docker run` / docker-compose working, where PORT is unset and a bare $PORT
# would expand to an empty string and crash uvicorn.
CMD uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
