# Operations Runbook - Iris Classification Service

This runbook provides operational guidance for deploying, monitoring, and troubleshooting the Iris Classification ML service.

## Table of Contents
1. [Dependency Pinning Strategy](#dependency-pinning-strategy)
2. [Image Optimization](#image-optimization)
3. [Security Considerations](#security-considerations)
4. [CI/CD Workflow](#cicd-workflow)
5. [Versioning Strategy](#versioning-strategy)
6. [Troubleshooting Guide](#troubleshooting-guide)

---

## Dependency Pinning Strategy

### Why We Pin Dependencies

Pinned dependencies ensure reproducibility across environments and prevent unexpected breakages from upstream package updates.

### Our Approach

**requirements.txt with exact versions:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
scikit-learn==1.4.0
numpy==1.26.3
joblib==1.3.2
```

### Updating Dependencies
```bash
# Update a specific package
pip install --upgrade fastapi==0.110.0
pip freeze > app/requirements.txt

# Test thoroughly before committing
pytest tests/ -v
docker build -t iris-classifier:test .
docker run -p 8000:8000 iris-classifier:test
```

### Benefits
- Reproducible builds across all environments
- No surprise breakages from dependency updates
- Easier debugging when issues arise
- Clear dependency audit trail

---

## Image Optimization

### Optimization Techniques Applied

#### 1. Multi-Stage Build

**Before (Single-stage):** ~1.2 GB
```dockerfile
FROM python:3.11
RUN pip install scikit-learn fastapi uvicorn
COPY . .
CMD ["uvicorn", "app:app"]
```

**After (Multi-stage):** 637 MB (47% reduction)
```dockerfile
# Builder stage - discarded after build
FROM python:3.11-slim AS builder
WORKDIR /build
RUN pip install scikit-learn joblib
RUN python train_model.py

# Runtime stage - only this ships
FROM python:3.11-slim
COPY --from=builder /build/model.pkl .
RUN pip install fastapi uvicorn joblib numpy
COPY app/ .
CMD ["uvicorn", "app:app"]
```

**Savings:** ~563 MB (47% smaller)

#### 2. Slim Base Image

- Using `python:3.11-slim` instead of `python:3.11`
- Removes unnecessary system packages
- **Savings:** ~300 MB per stage

#### 3. Layer Caching Strategy

Order of operations optimized for Docker layer caching:
```dockerfile
COPY requirements.txt .          # Changes rarely
RUN pip install -r requirements.txt  # Cached unless requirements change
COPY app/ .                      # Changes frequently
```

#### 4. .dockerignore

Excludes unnecessary files from build context:
```
venv/
__pycache__/
*.pyc
.git/
tests/
```

**Result:** Faster builds, smaller context

### Image Size Metrics

| Metric | Value |
|--------|-------|
| Final Image Size | 637 MB |
| Compressed Size | 140 MB |
| Base Image | python:3.11-slim |
| Layers | 12 |

---

## Security Considerations

### 1. Non-Root User

Container runs as `appuser` (UID 1000), not root:
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

**Why:** Limits damage if container is compromised.

### 2. Minimal Attack Surface

- Using slim base images
- Only installing required runtime dependencies
- No development tools in production image

### 3. Dependency Scanning

**Recommended:** Integrate vulnerability scanning in CI/CD
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: iris-classifier:latest
```

### 4. Secrets Management

- Using GitHub Secrets for registry credentials
- No hardcoded credentials in code or Dockerfile
- `GITHUB_TOKEN` used for authentication

### 5. Health Checks

Built-in Docker health check:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

**Monitoring:** Container orchestrators (Docker, Kubernetes) use this to restart unhealthy containers.

---

## CI/CD Workflow

### Pipeline Architecture
```
┌─────────────────┐
│  Git Tag Push   │
│    (v1.0.0)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Test Job      │
│  - Setup Python │
│  - Install deps │
│  - Train model  │
│  - Run pytest   │
└────────┬────────┘
         │
    [Tests Pass?]
         │
         ▼
┌─────────────────┐
│ Build & Push    │
│  - Build image  │
│  - Tag version  │
│  - Push to GHCR │
└─────────────────┘
```

### Step-by-Step Workflow

#### Job 1: Test
```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - Checkout code
    - Setup Python 3.11
    - Install dependencies
    - Train model
    - Run pytest tests
```

**Purpose:** Ensure code quality before building image

#### Job 2: Build and Push
```yaml
build-and-push:
  needs: test  # Only runs if tests pass
  runs-on: ubuntu-latest
  if: startsWith(github.ref, 'refs/tags/v')
  steps:
    - Checkout code
    - Setup Docker Buildx
    - Login to GitHub Container Registry
    - Extract version from tag
    - Build and push image
```

**Purpose:** Build optimized image and publish to registry

### Triggering the Pipeline
```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0

# Watch the workflow
# Visit: https://github.com/devp3102/ids568-mlops/actions
```

### Registry Authentication

Uses `GITHUB_TOKEN` (automatically provided by GitHub Actions):
```yaml
- name: Log in to GitHub Container Registry
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

**No manual setup required** - token is auto-generated per workflow run.

---

## Versioning Strategy

### Semantic Versioning (SemVer)

We follow semantic versioning: `vMAJOR.MINOR.PATCH`

**Examples:**
- `v1.0.0` - Initial release
- `v1.0.1` - Bug fix (model accuracy improvement)
- `v1.1.0` - New feature (additional endpoint)
- `v2.0.0` - Breaking change (API redesign)

### Tagging Strategy
```bash
# Patch release (bug fixes)
git tag v1.0.1
git push origin v1.0.1

# Minor release (new features)
git tag v1.1.0
git push origin v1.1.0

# Major release (breaking changes)
git tag v2.0.0
git push origin v2.0.0
```

### Image Tags

Each version creates two image tags:
1. **Specific version:** `ghcr.io/username/iris-classifier:v1.0.0`
2. **Latest:** `ghcr.io/username/iris-classifier:latest`

**Best Practice:**
- Development: Use `latest`
- Production: Use specific version tags (e.g., `v1.0.0`)

---

## Troubleshooting Guide

### Issue 1: Container Fails to Start

**Symptoms:**
```bash
docker logs iris-api
# Error: Model file not found at /app/app/model.pkl
```

**Diagnosis:**
```bash
# Check if model exists in image
docker run --rm iris-classifier:v1.0.0 ls -la /app/app/

# Verify MODEL_PATH environment variable
docker run --rm iris-classifier:v1.0.0 env | grep MODEL_PATH
```

**Solution:**
```bash
# Rebuild image to ensure model is included
docker build -t iris-classifier:v1.0.0 .

# Verify build completed both stages
docker build -t iris-classifier:v1.0.0 . | grep "Stage"
```

---

### Issue 2: Tests Pass Locally but Fail in CI

**Symptoms:**
- `pytest tests/ -v` passes locally
- GitHub Actions workflow fails on test job

**Common Causes:**
1. **Missing model file in CI**
2. **Different Python version**
3. **Path issues**

**Solution:**
```yaml
# Ensure model is trained in CI
- name: Train model for tests
  working-directory: module3/milestone2/app
  run: python train_model.py

# Verify Python version matches
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Must match local
```

---

### Issue 3: Docker Build is Slow

**Symptoms:**
- Build takes >5 minutes
- "Sending build context" takes long

**Diagnosis:**
```bash
# Check build context size
docker build --no-cache -t iris-classifier:v1.0.0 . 2>&1 | grep "Sending build context"
```

**Solutions:**

1. **Add to .dockerignore:**
```
venv/
__pycache__/
*.pyc
.git/
```

2. **Use build cache:**
```bash
# Rebuilds use cached layers
docker build -t iris-classifier:v1.0.0 .
```

3. **Use BuildKit:**
```bash
DOCKER_BUILDKIT=1 docker build -t iris-classifier:v1.0.0 .
```

---

### Issue 4: "ModuleNotFoundError" in Container

**Symptoms:**
```
ModuleNotFoundError: No module named 'sklearn'
```

**Cause:** scikit-learn not installed in runtime stage

**Solution:**
```dockerfile
# Ensure scikit-learn is in runtime dependencies
RUN pip install --no-cache-dir \
    fastapi==0.109.0 \
    scikit-learn==1.4.0  # Must be here!
```

---

### Issue 5: High Memory Usage

**Symptoms:**
- Container uses >1GB RAM
- OOM (Out of Memory) errors

**Diagnosis:**
```bash
# Check container memory usage
docker stats iris-api
```

**Solutions:**

1. **Set memory limits:**
```bash
docker run -d -p 8000:8000 --memory="512m" iris-classifier:v1.0.0
```

2. **Optimize model:**
```python
# Use smaller n_estimators
model = RandomForestClassifier(n_estimators=50)  # Instead of 100
```

---

### Issue 6: CI/CD Pipeline Doesn't Trigger

**Symptoms:**
- Push tag but workflow doesn't run

**Checklist:**
1. Tag matches pattern `v*`
2. Workflow file is in `.github/workflows/`
3. Workflow file is valid YAML

**Verify:**
```bash
# Check tag format
git tag
# Should show: v1.0.0 (not 1.0.0)

# Validate YAML
python -c "import yaml; yaml.safe_load(open('.github/workflows/build.yml'))"
```

**Fix:**
```bash
# Delete wrong tag
git tag -d 1.0.0
git push origin :refs/tags/1.0.0

# Create correct tag
git tag v1.0.0
git push origin v1.0.0
```

---

### Issue 7: Image Won't Pull from Registry

**Symptoms:**
```bash
docker pull ghcr.io/username/iris-classifier:v1.0.0
# Error: unauthorized
```

**Solution:**

1. **Make package public:**
   - Go to https://github.com/USERNAME?tab=packages
   - Click on `iris-classifier`
   - Settings → Change visibility → Public

2. **Or authenticate:**
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker pull ghcr.io/username/iris-classifier:v1.0.0
```

---

## Quick Reference Commands

### Local Development
```bash
# Train model
python app/train_model.py

# Run app
python app/app.py

# Run tests
pytest tests/ -v
```

### Docker
```bash
# Build
docker build -t iris-classifier:v1.0.0 .

# Run
docker run -d -p 8000:8000 --name iris-api iris-classifier:v1.0.0

# Logs
docker logs iris-api

# Stop
docker stop iris-api && docker rm iris-api
```

### Git & CI/CD
```bash
# Tag and trigger pipeline
git tag v1.0.0
git push origin v1.0.0

# View tags
git tag -l
```

---

## Monitoring & Observability

### Health Checks
```bash
# Manual health check
curl http://localhost:8000/health

# Continuous monitoring
watch -n 5 'curl -s http://localhost:8000/health | jq'
```

### Logs
```bash
# Follow logs
docker logs -f iris-api

# Last 100 lines
docker logs --tail 100 iris-api
```

### Metrics
```bash
# Container stats
docker stats iris-api

# Disk usage
docker system df
```

---


