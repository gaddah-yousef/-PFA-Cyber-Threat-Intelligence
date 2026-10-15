FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY main.py .
COPY alembic.ini .
COPY alembic ./alembic
COPY docker-entrypoint.sh .

RUN groupadd --system app && useradd --system --gid app --home /app app \
    && chmod +x docker-entrypoint.sh \
    && mkdir -p /data && chown -R app:app /app /data

USER app

EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
