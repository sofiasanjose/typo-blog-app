## Multi-stage Dockerfile for typo-blog-app

# --- Builder: create wheels to speed up final image installs
FROM python:3.9-slim AS builder
WORKDIR /wheels
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /tmp/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && python -m pip install --upgrade pip wheel setuptools \
    && pip wheel --no-deps --wheel-dir /wheels -r /tmp/requirements.txt \
    && apt-get purge -y --auto-remove build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# --- Final image: lean runtime
FROM python:3.9-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies from built wheels and gunicorn
COPY --from=builder /wheels /wheels
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir /wheels/* gunicorn

# Copy app source
COPY . /app

# Expose default port used by the app
EXPOSE 8000

# Default command: run via gunicorn binding port 8000
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8000", "typo.app:app"]
