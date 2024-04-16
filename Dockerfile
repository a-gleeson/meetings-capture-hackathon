FROM python:3.10-slim as builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN apt-get update -y && apt-get install -y gcc g++ && \
    # Prevent apt-get cache from being persisted to this layer.
    rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install poetry

COPY poetry.lock* pyproject.toml /app/

COPY . /app/

RUN poetry install --no-interaction --only main --no-ansi
#--no-root --sync

# ---- Run Stage ----
FROM python:3.10-slim as runner

WORKDIR /app

COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

EXPOSE 8501

CMD ["streamlit", "run", "app/home.py"]