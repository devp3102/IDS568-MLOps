# ============================================
# Stage 1: Builder - Train the model
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy training requirements
COPY app/requirements.txt .

# Install training dependencies
RUN pip install --user --no-cache-dir \
    scikit-learn==1.4.0 \
    joblib==1.3.2

# Copy training script
COPY app/train_model.py .

# Train the model (creates model.pkl in /build)
RUN python train_model.py

# ============================================
# Stage 2: Runtime - Serve predictions
# ============================================
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy requirements
COPY app/requirements.txt .

# Install runtime dependencies (including scikit-learn for model loading)
RUN pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    pydantic==2.5.3 \
    scikit-learn==1.4.0 \
    joblib==1.3.2 \
    numpy==1.26.3

# Copy application code - maintain package structure
COPY app/ ./app/

# Copy trained model from builder stage into app directory
COPY --from=builder /build/model.pkl ./app/model.pkl

# Set environment variable for model path
ENV MODEL_PATH=/app/app/model.pkl

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]