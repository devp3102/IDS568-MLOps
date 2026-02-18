from pydantic import BaseModel, Field
from typing import Literal

class IrisInput(BaseModel):
    sepal_length: float = Field(..., ge=0, le=10, description="Sepal length in cm")
    sepal_width: float = Field(..., ge=0, le=10, description="Sepal width in cm")
    petal_length: float = Field(..., ge=0, le=10, description="Petal length in cm")
    petal_width: float = Field(..., ge=0, le=10, description="Petal width in cm")

    class Config:
        json_schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2
            }
        }

class PredictionResponse(BaseModel):
    species: Literal["setosa", "versicolor", "virginica"]
    confidence: float
    probabilities: dict[str, float]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str

class RootResponse(BaseModel):
    status: str
    service: str
    version: str
    model_loaded: bool