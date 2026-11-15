# syntax=docker/dockerfile:1.7
# Multi-stage: build the app's wheel once, ship a slim image that runs as a non-root user.
FROM python:3.12-slim AS build
WORKDIR /src
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY pyproject.toml ./
COPY main.py ./
COPY app ./app
RUN pip wheel --wheel-dir /wheels .

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8070
RUN useradd --create-home --uid 10001 app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir --no-index /wheels/* && rm -rf /wheels
USER app
WORKDIR /home/app
# These run from the working directory: `alembic upgrade head` and `python scripts/publish_week.py` before the
# service, then the publishing script again every Monday
COPY main.py alembic.ini ./
COPY migrations ./migrations
COPY scripts ./scripts
EXPOSE 8070
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health', timeout=3)"
# Nothing lives in the process (bookings in Postgres, the rate limit in Redis), so workers can be added freely
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --no-access-log --workers 2"]
