# tests/test_app.py
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add the parent directory (Milestone 2) to path
milestone_dir = Path(__file__).parent.parent
sys.path.insert(0, str(milestone_dir))

# Now import from app package
from app.app import app

# Use TestClient with context manager to trigger lifespan
@pytest.fixture(scope="module")
def client():
    """Create test client with lifespan context."""
    with TestClient(app) as c:
        yield c

def test_read_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True

def test_predict_setosa(client):
    """Test prediction for Iris setosa."""
    response = client.post(
        "/predict",
        json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["species"] == "setosa"
    assert data["confidence"] > 0.5
    assert "probabilities" in data
    assert len(data["probabilities"]) == 3

def test_predict_versicolor(client):
    """Test prediction for Iris versicolor."""
    response = client.post(
        "/predict",
        json={
            "sepal_length": 6.4,
            "sepal_width": 3.2,
            "petal_length": 4.5,
            "petal_width": 1.5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["species"] == "versicolor"
    assert data["confidence"] > 0.5

def test_predict_virginica(client):
    """Test prediction for Iris virginica."""
    response = client.post(
        "/predict",
        json={
            "sepal_length": 7.2,
            "sepal_width": 3.0,
            "petal_length": 5.8,
            "petal_width": 1.6
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["species"] == "virginica"
    assert data["confidence"] > 0.5

def test_predict_invalid_input(client):
    """Test prediction with invalid input (negative values)."""
    response = client.post(
        "/predict",
        json={
            "sepal_length": -1.0,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        }
    )
    assert response.status_code == 422

def test_predict_missing_field(client):
    """Test prediction with missing required field."""
    response = client.post(
        "/predict",
        json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4
        }
    )
    assert response.status_code == 422

def test_predict_out_of_range(client):
    """Test prediction with out of range values."""
    response = client.post(
        "/predict",
        json={
            "sepal_length": 15.0,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        }
    )
    assert response.status_code == 422