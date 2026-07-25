FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SIEVE_HOST=0.0.0.0 \
    SIEVE_PORT=8765 \
    SIEVE_DB=/data/sieve.sqlite \
    SIEVE_DATA_ROOT=/suites \
    SIEVE_ALLOW_REMOTE=1

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 sieve \
    && mkdir -p /data /suites \
    && chown -R sieve:sieve /data /suites

USER sieve
EXPOSE 8765
VOLUME ["/data", "/suites"]
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/readyz', timeout=2)"
CMD ["sieve", "serve"]
