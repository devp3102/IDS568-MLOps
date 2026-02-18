# Iris Classification ML Service

A containerized machine learning service for iris flower species classification using Random Forest.

![CI/CD](https://github.com/devp3102/ids568-mlops/workflows/Build%20and%20Test/badge.svg)

## Overview

This project implements a production-ready ML inference API using FastAPI, scikit-learn, and Docker with automated CI/CD.

## Features

- RESTful API with FastAPI
- Random Forest classifier (100% test accuracy)
- Multi-stage Docker build (637MB optimized image)
- Automated CI/CD with GitHub Actions
- Health check endpoints
- Interactive API documentation (Swagger UI)
- Non-root container user for security
- Comprehensive unit tests

## Quick Start

### Pull and Run with Docker
```bash
# Pull the image from GitHub Container Registry
docker pull ghcr.io/devp3102/iris-classifier:latest

# Run the container
docker run -d -p 8000:8000 --name iris-api ghcr.io/devp3102/iris-classifier:latest

# Test the health endpoint
curl http://localhost:8000/health

# Stop the container
docker stop iris-api
docker rm iris-api
```

### Local Development
```bash
# Clone the repository
git clone https://github.com/devp3102/ids568-mlops.git
cd ids568-mlops

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt
pip install pytest httpx

# Train the model
python app/train_model.py

# Run the application
python app/app.py

# Run tests
pytest tests/ -v
```

## API Endpoints

### GET /
Health check endpoint returning service status.

**Response:**
```json
{
  "status": "healthy",
  "service": "iris-classification",
  "version": "1.0.0",
  "model_loaded": true
}
```

### GET /health
Detailed health check with model status.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "/app/app/model.pkl"
}
```

### POST /predict
Predict iris species from flower measurements.

**Request:**
```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

**Response:**
```json
{
  "species": "setosa",
  "confidence": 1.0,
  "probabilities": {
    "setosa": 1.0,
    "versicolor": 0.0,
    "virginica": 0.0
  }
}
```

## Interactive Documentation

Visit http://localhost:8000/docs for Swagger UI with interactive API testing.

## Building from Source
```bash
# Build the Docker image
docker build -t iris-classifier:v1.0.0 .

# Run the container
docker run -d -p 8000:8000 iris-classifier:v1.0.0

# Check logs
docker logs <container_id>
```

## Project Structure
```
milestone2/
├── .github/
│   └── workflows/
│       └── build.yml          # CI/CD pipeline
├── app/
│   ├── __init__.py           # Package initialization
│   ├── app.py                # FastAPI application
│   ├── schemas.py            # Pydantic models
│   ├── train_model.py        # Model training script
│   ├── requirements.txt      # Python dependencies
│   └── model.pkl            # Trained model (generated)
├── tests/
│   └── test_app.py          # Unit tests
├── .dockerignore            # Docker build exclusions
├── Dockerfile               # Multi-stage build definition
├── README.md                # Project documentation
└── RUNBOOK.md              # Operations guide
```

## Model Information

- **Algorithm**: Random Forest Classifier
- **Dataset**: Iris dataset (sklearn)
- **Features**: 4 (sepal_length, sepal_width, petal_length, petal_width)
- **Classes**: 3 (setosa, versicolor, virginica)
- **Training Accuracy**: 100%
- **Test Accuracy**: 100%

## CI/CD Pipeline

The GitHub Actions workflow automatically:
1. Runs unit tests with pytest
2. Builds multi-stage Docker image
3. Pushes to GitHub Container Registry with semantic versioning
4. Tags images with both version number and `latest`

**Triggered on:** Git tags matching `v*` pattern (e.g., v1.0.0)

## Environment Variables

- `MODEL_PATH`: Path to trained model file (default: `/app/app/model.pkl`)