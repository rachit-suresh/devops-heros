# syntax=docker/dockerfile:1

# Build stage: resolve and install dependencies into an isolated venv.
FROM python:3.12-slim AS deps
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y pip

# Runtime stage: no pip, no build tooling, non-root user.
FROM python:3.12-slim
RUN useradd --uid 10001 --create-home appuser
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=deps /opt/venv /opt/venv
WORKDIR /app
COPY --chown=appuser:appuser . .
USER 10001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
