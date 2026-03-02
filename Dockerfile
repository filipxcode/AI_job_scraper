FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python -m venv /opt/venv

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN useradd -m -u 10001 appuser

COPY --chown=appuser:appuser . .

USER appuser

ENTRYPOINT ["python", "main.py"]
CMD ["--mode", "all"]