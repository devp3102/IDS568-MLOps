from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os
import numpy as np

PORT = int(os.getenv("PORT", "8000"))
MODEL_PATH = os.getenv("MODEL_PATH", "model.pkl")

model = joblib.load("model.pkl")
app = FastAPI(title="Iris Classification API")

class PredictRequest(BaseModel):
    features: list[float]

class PredictResponse(BaseModel):
    prediction: int
    species: str

# Species names mapping
SPECIES_NAMES = ["Setosa", "Versicolor", "Virginica"]

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Predict iris species from input features.

    """
    # Convert features to numpy array for prediction
    features_array = np.array([request.features])
    
    # Make prediction using the pre-loaded model
    prediction = model.predict(features_array)[0]
    
    # Get species name
    species = SPECIES_NAMES[prediction]
    
    # Return response matching PredictResponse schema
    return PredictResponse(
        prediction=int(prediction),
        species=species
    )