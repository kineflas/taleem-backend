# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Runtime deps: PostgreSQL client + ffmpeg (audio conversion for admin recorder)
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code + startup script
COPY . .
COPY start.sh .
RUN chmod +x start.sh

# Ensure audio upload directory exists
RUN mkdir -p /app/static/audio

# Generate real Husary word-level timestamps for karaoke (offline data)
RUN python scripts/generate_audio_timings.py \
    && rm -rf scripts/.cache

# Non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["./start.sh"]
