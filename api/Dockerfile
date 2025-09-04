# Use Flox-generated base image
FROM ghcr.io/flox/flox:latest AS flox

# Copy project files
WORKDIR /app
COPY . .

# Activate Flox environment and install dependencies
RUN flox activate

# API-specific configuration
ENV PYTHONPATH=/app
ENV API_HOST=0.0.0.0
ENV API_PORT=8000

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run API server
CMD ["flox", "activate", "--", "python", "run_api.py"]