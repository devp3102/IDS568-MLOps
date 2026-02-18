# app/app.py
from pathlib import Path
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import joblib
import numpy as np
import os

from app.schemas import IrisInput, PredictionResponse, HealthResponse, RootResponse

model = None
MODEL_PATH = os.getenv("MODEL_PATH", str(Path(__file__).parent / "model.pkl"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    try:
        model = joblib.load(MODEL_PATH)
        print(f"Model loaded successfully from {MODEL_PATH}")
    except FileNotFoundError:
        print(f"Error: Model file not found at {MODEL_PATH}")
        raise
    except Exception as e:
        print(f"Error loading model: {e}")
        raise
    
    yield 
    

app = FastAPI(
    title="Iris Classification API", 
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/", response_model=RootResponse)
def read_root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "iris-classification",
        "version": "1.0.0",
        "model_loaded": model is not None
    }

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(input_data: IrisInput):
    """Predict iris species from measurements."""
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail="Model not loaded. Please ensure model.pkl exists."
        )
    
    # Prepare input features
    features = np.array([[
        input_data.sepal_length,
        input_data.sepal_width,
        input_data.petal_length,
        input_data.petal_width
    ]])
    
    # Make prediction
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    
    # Map to species names (LOWERCASE to match schema)
    species_names = ["setosa", "versicolor", "virginica"]
    species = species_names[prediction]
    confidence = float(probabilities[prediction])
    
    prob_dict = {
        species_names[i]: float(probabilities[i]) 
        for i in range(len(species_names))
    }
    
    return PredictionResponse(
        species=species,
        confidence=confidence,
        probabilities=prob_dict
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
