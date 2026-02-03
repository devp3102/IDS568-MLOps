# Milestone 1: Web & Serverless Model Serving

This project demonstrates ML model deployment using two different patterns: containerized FastAPI service on Cloud Run and serverless Cloud Functions.

## Project Overview

An iris flower classification model (Random Forest) deployed via:
1. **FastAPI + Docker on Google Cloud Run** (containerized web service)
2. **Cloud Functions** (serverless function-as-a-service)

Both deployments expose the same prediction endpoint with identical input/output schemas.

---

## Repository Structure
```
Milestone 1/
├── main.py                    # FastAPI application
├── model.pkl                  # Trained Random Forest model
├── requirements.txt           # Python dependencies (pinned versions)
├── Dockerfile                 # Container definition for Cloud Run
├── train_model.py             # Model training script
├── cloud_function/            # Cloud Function deployment
│   ├── main.py               # Function entry point
│   ├── requirements.txt      # Function dependencies
│   └── model.pkl             # Model artifact (copy)
├── screenshots/               # Deployment evidence
│   ├── cloud_run_response.png
│   ├── cloud_function_logs.png
│   └── benchmark_results.png
└── README.md                  
```

**Note:** `cloud_function/model.pkl` is a copy of the root `model.pkl`, required for Cloud Function deployment as the function needs access to the model artifact.

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Docker Desktop
- Google Cloud SDK (gcloud CLI)
- GCP account with billing enabled

### Local Development

1. **Clone the repository and navigate to project directory**
```bash
cd "Milestone 1"
```

2. **Create virtual environment and install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Train the model (or use existing model.pkl)**
```bash
python3 train_model.py
```

4. **Run FastAPI locally**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Test the local endpoint**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

Expected response:
```json
{"prediction":0,"species":"Setosa"}
```

---

## Deployment

### Cloud Run Deployment

1. **Build Docker image for AMD64 (Cloud Run architecture)**
```bash
docker build --platform linux/amd64 -t iris-api:latest .
```

2. **Configure GCP and Artifact Registry**
```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable artifactregistry.googleapis.com run.googleapis.com

# Create Artifact Registry repository
gcloud artifacts repositories create ml-models \
  --repository-format=docker \
  --location=us-central1

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

3. **Tag and push image**
```bash
docker tag iris-api:latest \
  us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ml-models/iris-api:v1

docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ml-models/iris-api:v1
```

4. **Deploy to Cloud Run**
```bash
gcloud run deploy iris-classifier \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/ml-models/iris-api:v1 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

### Cloud Function Deployment

1. **Navigate to cloud_function directory**
```bash
cd cloud_function
```

2. **Deploy function**
```bash
gcloud functions deploy iris-predict \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --source . \
  --entry-point predict \
  --trigger-http \
  --allow-unauthenticated \
  --memory 512MB \
  --timeout 540s
```

**Note:** Extended timeout (540s) is required for model loading during cold starts.

---

## Deployment URLs

**Cloud Run Service:**  
https://iris-classifier-259701213418.us-central1.run.app


**Cloud Function:**  
https://us-central1-mlops-milestone1-486301.cloudfunctions.net/iris-predict

---

## API Usage

### Request Format

**Endpoint:** `POST /predict`

**Request Body:**
```json
{
  "features": [5.1, 3.5, 1.4, 0.2]
}
```

**Response:**
```json
{
  "prediction": 0,
  "species": "Setosa"
}
```

### Example Usage

**Cloud Run:**
```bash
curl -X POST "YOUR_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

**Cloud Function:**
```bash
curl -X POST "YOUR_URL/iris-predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

### Interactive Testing (Cloud Run Only)

Cloud Run deployment includes FastAPI's automatic interactive documentation:

1. Open `https://iris-classifier-xxx.run.app/docs` in your browser
2. Click on the `/predict` endpoint
3. Click "Try it out"
4. Edit the JSON request body with your feature values
5. Click "Execute" to see results

**Note:** Cloud Functions do not provide automatic interactive documentation.

### Input Validation

The API uses Pydantic for automatic validation:
- `features` must be a list of 4 floats
- Invalid input returns HTTP 422 with error details

**Example invalid request:**
```bash
curl -X POST "https://iris-classifier-xxx.run.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": "invalid"}'
```

Returns:
```json
{
  "detail": [
    {
      "loc": ["body", "features"],
      "msg": "value is not a valid list",
      "type": "type_error.list"
    }
  ]
}
```

---

## ML Lifecycle Position

This deployment demonstrates the **serving stage** of the ML lifecycle:
```
Data Collection → Feature Engineering → Model Training → Model Validation
                                                              ↓
                                                        [Model Artifact]
                                                              ↓
                                        Deployment (FastAPI/Cloud Functions) ← [YOU ARE HERE]
                                                              ↓
                                                    Production Inference
                                                              ↓
                                              Monitoring & Model Updates
```

**Lifecycle Context:**
- **Input:** Trained model artifact (`model.pkl`) from training pipeline
- **Processing:** Model loading, schema validation, inference
- **Output:** REST API accessible to downstream consumers
- **Monitoring touchpoints:** Request logging, latency tracking, prediction distribution

---

## Comparative Analysis: Cloud Run vs Cloud Functions

### Deployment Architecture

| Aspect | Cloud Run | Cloud Functions |
|--------|-----------|-----------------|
| **Deployment Unit** | Docker container | Source code |
| **Build Process** | Manual Docker build | Automatic build by GCP |
| **Environment Control** | Full (Dockerfile) | Limited (runtime constraints) |
| **Artifact Registry** | Required | Not required |
| **Interactive Documentation** | Yes (FastAPI /docs) | No |

### Latency Characteristics

**Benchmark Results:**

| Metric | Cloud Run | Cloud Function |
|--------|-----------|----------------|
| **Cold Start** | 10.189s | 7.416s |
| **Warm Request** | 0.112s | 0.120s |
| **Cold Start Penalty** | ~90x | ~62x |

**Key Observations:**
- Cloud Functions has **~27% faster cold start** (7.4s vs 10.2s)
- Warm latency is nearly identical (~110-120ms)
- Both cold starts are dominated by model loading time

**Why Cloud Functions Has Faster Cold Start:**
- Cloud Run must pull and start entire container image
- Cloud Functions loads source code directly without container overhead
- However, difference narrows with smaller base images

### Lifecycle Differences

**Cloud Run (Stateful Container):**
- Model loaded once per container instance
- Container persists between requests
- Can maintain in-memory state (caching, connections)
- Supports up to 80+ concurrent requests per instance
- Full control over startup process via Dockerfile

**Cloud Functions (Stateless):**
- Model loaded once per function instance
- Global variable caching works but with limitations
- Designed for single request per instance (Gen1)
- Each invocation is isolated
- Platform-managed startup and runtime

### Artifact Loading Strategies

**Cloud Run:**
```python
# Loaded at module level when container starts
model = joblib.load("model.pkl")

@app.post("/predict")
def predict(request):
    return model.predict(...)  # Model already in memory
```

**Cloud Functions:**
```python
# Global caching pattern
model = None

def load_model():
    global model
    if model is None:
        model = joblib.load("model.pkl")
    return model

@functions_framework.http
def predict(request):
    clf = load_model()  # Cached after first call
    return clf.predict(...)
```

**Key Difference:**
- Cloud Run: Explicit control over when/how model loads
- Cloud Functions: Relies on global variable caching pattern

### When to Use Each

**Choose Cloud Run when:**
- Latency SLAs require <200ms response times
- Model artifact is large (>100MB)
- Need custom system dependencies or compiled libraries
- Require fine-grained control over environment
- High, sustained traffic patterns
- Want interactive API documentation (/docs)
- Full reproducibility is critical

**Choose Cloud Functions when:**
- Traffic is sporadic (hours between requests)
- Cost optimization is priority over latency
- Model is small (<50MB) with pure Python dependencies
- Rapid prototyping and iteration needed
- Serverless simplicity preferred over container control
- Don't need interactive documentation

---

## Technical Details

### Model Information
- **Algorithm:** Random Forest Classifier
- **Dataset:** Iris (150 samples, 4 features, 3 classes)
- **Train/Test Split:** 70/30
- **Accuracy:** ~95%
- **Model Size:** ~185KB
- **Features:** Sepal length, sepal width, petal length, petal width (in cm)
- **Classes:** Setosa (0), Versicolor (1), Virginica (2)

### Dependencies

**Root requirements.txt (FastAPI/Cloud Run):**
```
fastapi==0.128.0
uvicorn==0.40.0
pydantic==2.12.5
scikit-learn==1.8.0
joblib==1.5.3
numpy==2.4.1
```

**cloud_function/requirements.txt:**
```
functions-framework==3.10.0
flask==3.1.2
scikit-learn==1.8.0
joblib==1.5.3
numpy==2.4.1
```

---

## Troubleshooting

### Common Issues

**Cloud Run deployment fails with "unsupported architecture":**
- Solution: Rebuild with `--platform linux/amd64` flag
- Reason: Apple Silicon Macs (M1/M2/M3) use ARM64, Cloud Run uses AMD64

**Cloud Function cold start timeout:**
- Solution: Increase timeout with `--timeout 540s` flag
- Reason: Model loading requires extended startup time (~7-10 seconds)

**Port binding errors:**
- Cloud Run expects `PORT` environment variable (default 8080)
- Ensure Dockerfile CMD uses `$PORT` or hardcode 8080
- Local testing: use `--port 8000` for consistency

**Permission denied errors:**
- Run: `gcloud auth configure-docker us-central1-docker.pkg.dev`
- Ensure billing is enabled on GCP project
- Check IAM permissions for Cloud Run/Functions deployment

**"Not Found" when accessing root URL:**
- This is expected! The API only has `/predict` endpoint
- Access `/docs` for interactive documentation (Cloud Run only)
- Use POST requests with JSON body to `/predict`

**Cloud Function returns "Missing 'features' in request":**
- This is correct validation behavior!
- Ensure you're sending POST request with proper JSON body
- Example: `{"features": [5.1, 3.5, 1.4, 0.2]}`

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Google Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [GCP Artifact Registry](https://cloud.google.com/artifact-registry/docs)

---
