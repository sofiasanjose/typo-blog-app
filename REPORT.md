# Assignment 2: DevOps Implementation Report
## Typo Blog Application

**Student**: Sofia Claudia San Jose Bonoan  
**Repository**: https://github.com/sofiasanjose/typo-blog-app  
**Deployed Application**: https://sof-typo-webapp-2004.azurewebsites.net  
**Date**: November 28, 2025

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Code Quality Improvements](#code-quality-improvements)
3. [Testing Implementation](#testing-implementation)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Containerization](#containerization)
6. [Cloud Deployment](#cloud-deployment)
7. [Monitoring Setup](#monitoring-setup)
8. [Project Structure](#project-structure)
9. [Instructions for Running](#instructions-for-running)
10. [Challenges and Solutions](#challenges-and-solutions)

---

## Executive Summary

This report documents the implementation of DevOps practices for the Typo Blog application as part of Assignment 2. The project successfully achieves all required objectives:

- ✅ **Code Quality**: Implemented linting with Ruff, achieving zero linting errors
- ✅ **Testing**: Comprehensive test suite with 72% code coverage (exceeds 70% requirement)
- ✅ **CI Pipeline**: Automated testing, linting, and Docker builds on every push/PR
- ✅ **CD Pipeline**: Automated deployment to Azure Web App for Containers
- ✅ **Containerization**: Multi-stage Dockerfile with production-ready configuration
- ✅ **Cloud Deployment**: Successfully deployed to Azure using Container Registry
- ✅ **Monitoring**: Prometheus metrics endpoints with Grafana dashboard configuration

**Live Application**: https://sof-typo-webapp-2004.azurewebsites.net

---

## Code Quality Improvements

### Linting Implementation

**Tool**: Ruff (modern Python linter, faster than Flake8 and Black combined)

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py39"
```

**Results**:
- All files pass linting checks with zero errors
- Enforces consistent code style across the codebase
- Integrated into CI pipeline to prevent code quality regressions

**Command to run linting**:
```bash
ruff check typo/
```

### Code Refactoring

Key improvements made to `typo/app.py`:
1. Added type hints for better code documentation
2. Improved error handling with global exception handler
3. Separated concerns (models, storage, API endpoints)
4. Added comprehensive docstrings

---

## Testing Implementation

### Test Coverage: 72%

**Testing Framework**: pytest with pytest-cov

**Test Files Created**:

1. **`tests/test_models.py`** - Unit tests for data models
   - BlogPost serialization/deserialization
   - BlogCustomization data validation
   
2. **`tests/test_storage.py`** - Storage layer tests
   - JSON file read/write operations
   - Data persistence validation
   
3. **`tests/test_api.py`** - API integration tests
   - POST /api/posts (create post)
   - GET /api/posts (list posts)
   - GET /api/posts/<id> (get single post)
   - PUT /api/posts/<id> (update post)
   - DELETE /api/posts/<id> (delete post)
   
4. **`tests/test_uploads.py`** - File upload tests
   - Multipart form data handling
   - File type validation
   
5. **`tests/test_customize.py`** - Customization tests
   - Theme customization POST
   - Settings persistence

### Running Tests

**Run all tests**:
```bash
pytest
```

**Run with coverage report**:
```bash
pytest --cov=typo --cov-report=term-missing
```

**Coverage Report**:
```
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
typo/app.py          156     43    72%   (various lines)
-------------------------------------------------
TOTAL                156     43    72%
```

### Test Results

All tests pass successfully:
- ✅ 15+ test cases
- ✅ 100% pass rate
- ✅ Coverage exceeds 70% requirement

---

## CI/CD Pipeline

### Continuous Integration (CI)

**Workflow File**: `.github/workflows/ci.yml`

**Triggers**:
- On push to any branch
- On pull requests to `main` branch

**CI Pipeline Steps**:

1. **Checkout Code** - Clone repository
2. **Set up Python 3.9** - Configure Python environment
3. **Cache Dependencies** - Speed up builds with pip caching
4. **Install Dependencies** - Install from `requirements.txt`
5. **Lint with Ruff** - Ensure code quality standards
6. **Run Tests** - Execute pytest with coverage ≥70% requirement
7. **Build Docker Image** - Verify containerization works

**Status**: ✅ All CI workflows passing

**Example Run**:
- Duration: ~45 seconds
- All checks passing
- Coverage: 72%

### Continuous Deployment (CD)

**Workflow File**: `.github/workflows/cd.yml`

**Triggers**:
- On push to `main` branch only

**CD Pipeline Steps**:

1. **Checkout Code**
2. **Set up Docker Buildx** - Enable multi-platform builds
3. **Login to Azure Container Registry** - Authenticate with ACR credentials
4. **Build and Push Docker Image** - Build multi-stage Dockerfile
   - Tag with commit SHA: `softypo2004.azurecr.io/typo-blog-app:<sha>`
   - Tag with latest: `softypo2004.azurecr.io/typo-blog-app:latest`

**Azure Web App Configuration**:
- Configured Deployment Center to pull from ACR
- Continuous deployment enabled
- Uses system-assigned managed identity for authentication
- Automatically pulls latest image on push

**Status**: ✅ Successfully deployed to Azure

---

## Containerization

### Dockerfile

**Type**: Multi-stage build for optimized production image

**Stage 1: Builder**
```dockerfile
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt
```

**Stage 2: Runtime**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
COPY typo/ ./typo/
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "typo.app:app"]
```

**Benefits**:
- Smaller final image size (excludes build tools)
- Production WSGI server (gunicorn)
- 2 worker processes for better performance
- Only includes necessary runtime files

### Docker Compose

**File**: `docker-compose.yml`

**Purpose**: Local development and testing

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./typo:/app/typo
    command: gunicorn --bind 0.0.0.0:8000 --reload typo.app:app
```

**Run locally**:
```bash
docker-compose up --build
```

### .dockerignore

Optimizes build by excluding:
- `__pycache__`
- `.venv`
- `tests/`
- `.git/`
- Development files

---

## Cloud Deployment

### Azure Infrastructure

**Platform**: Azure Web App for Containers

**Resources Created**:

1. **Azure Container Registry (ACR)**
   - Name: `softypo2004`
   - URL: `softypo2004.azurecr.io`
   - SKU: Basic
   - Admin enabled for GitHub Actions authentication

2. **App Service Plan**
   - Name: `sof-typo-plan`
   - OS: Linux
   - SKU: B1 (Basic)
   - Region: West Europe

3. **Web App**
   - Name: `sof-typo-webapp-2004`
   - URL: https://sof-typo-webapp-2004.azurewebsites.net
   - Runtime: Docker Container
   - Container Image: `softypo2004.azurecr.io/typo-blog-app:latest`

4. **Managed Identity**
   - Type: System-assigned
   - Role: AcrPull (for pulling images from ACR)

### Environment Configuration

**Application Settings**:
- `WEBSITES_PORT=8000` - Tells Azure which port the container exposes

### Deployment Process

1. **Developer pushes to main** → Triggers CD workflow
2. **GitHub Actions builds image** → Pushes to ACR with tags
3. **Azure Web App detects new image** → Pulls latest tag
4. **Container starts** → App becomes available
5. **Health check passes** → Deployment complete

### Verification

**Health Endpoint**: https://sof-typo-webapp-2004.azurewebsites.net/health
```json
{
  "status": "healthy",
  "uptime_seconds": 1234
}
```

**Metrics Endpoint**: https://sof-typo-webapp-2004.azurewebsites.net/metrics
- Returns Prometheus-formatted metrics
- Includes request counts, latency, errors, system metrics

---

## Monitoring Setup

### Metrics Implementation

**Library**: `prometheus_client`

**Metrics Exposed**:

1. **Request Count** (`typo_request_count_total`)
   - Type: Counter
   - Labels: method, endpoint, http_status
   - Tracks total number of HTTP requests

2. **Request Latency** (`typo_request_latency_seconds`)
   - Type: Histogram
   - Labels: method, endpoint
   - Tracks request processing time

3. **Error Count** (`typo_error_count_total`)
   - Type: Counter
   - Tracks application errors

4. **System Metrics** (automatic)
   - Python GC stats
   - Process memory usage
   - CPU time
   - Open file descriptors

### Endpoints

**Health Check**: `/health`
```json
{
  "status": "healthy",
  "uptime_seconds": 123
}
```

**Metrics**: `/metrics`
```
# HELP typo_request_count_total Total Request Count
# TYPE typo_request_count_total counter
typo_request_count_total{endpoint="/",http_status="200",method="GET"} 42.0
...
```

### Monitoring Configuration Files

**Location**: `monitoring/` directory

1. **`prometheus.yml`** - Prometheus scrape configuration
   - Scrapes `/metrics` every 10 seconds
   - Scrapes `/health` every 30 seconds
   - Targets: Azure Web App URL

2. **`docker-compose.monitoring.yml`** - Local monitoring stack
   - Runs Prometheus on port 9090
   - Runs Grafana on port 3000
   - Configured to scrape deployed app

3. **`grafana-dashboard.json`** - Pre-configured dashboard
   - 6 panels showing key metrics
   - Request rate, latency, errors, uptime, memory

4. **`README.md`** - Complete monitoring documentation

### Dashboard Panels

1. **Total HTTP Requests** - Request rate over time
2. **Request Latency (95th percentile)** - Response times
3. **Error Rate** - 4xx and 5xx errors
4. **App Uptime** - How long the app has been running
5. **Memory Usage** - Process memory consumption
6. **Request Count by Endpoint** - Traffic distribution

### Running Monitoring (Optional)

```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yml up
```

Then access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

---

## Project Structure

```
typo-blog-app/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Continuous Integration workflow
│       └── cd.yml                 # Continuous Deployment workflow
├── typo/                          # Main application code
│   ├── app.py                     # Flask application with Prometheus metrics
│   ├── customization.json         # Theme settings
│   ├── posts.json                 # Blog posts data
│   ├── static/                    # CSS, images, uploads
│   └── templates/                 # HTML templates
├── tests/                         # Test suite
│   ├── test_models.py            # Model unit tests
│   ├── test_storage.py           # Storage tests
│   ├── test_api.py               # API integration tests
│   ├── test_uploads.py           # Upload functionality tests
│   └── test_customize.py         # Customization tests
├── monitoring/                    # Monitoring artifacts
│   ├── prometheus.yml            # Prometheus configuration
│   ├── grafana-dashboard.json    # Grafana dashboard
│   ├── docker-compose.monitoring.yml
│   └── README.md                 # Monitoring documentation
├── docs/                          # Documentation
│   ├── planning.md               # Initial planning
│   └── report.md                 # Original report
├── Dockerfile                     # Multi-stage production image
├── docker-compose.yml            # Local development setup
├── .dockerignore                 # Docker build exclusions
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
├── README.md                     # Project documentation
└── REPORT.md                     # This file
```

---

## Instructions for Running

### Prerequisites

- Python 3.9+
- pip
- Git
- Docker (optional, for local containerized testing)

### Local Development

1. **Clone the repository**:
```bash
git clone https://github.com/sofiasanjose/typo-blog-app.git
cd typo-blog-app
```

2. **Create virtual environment**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the application**:
```bash
python -m flask --app typo.app run
```

5. **Access the app**:
- Main app: http://localhost:5000
- Health: http://localhost:5000/health
- Metrics: http://localhost:5000/metrics

### Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=typo --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py -v
```

### Running with Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build and run manually
docker build -t typo-blog-app .
docker run -p 8000:8000 typo-blog-app
```

### Running Linting

```bash
# Check code quality
ruff check typo/

# Auto-fix issues
ruff check typo/ --fix
```

### Deploying to Azure

Deployment is automated via GitHub Actions. To trigger:

1. **Push to main branch**:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

2. **GitHub Actions will**:
   - Run CI checks (lint, test, coverage)
   - Build Docker image
   - Push to Azure Container Registry
   - Azure Web App auto-deploys the new image

3. **Verify deployment**:
   - Check GitHub Actions status
   - Visit https://sof-typo-webapp-2004.azurewebsites.net

---

## Challenges and Solutions

### Challenge 1: Docker Not Available Locally
**Problem**: Local machine doesn't have Docker installed  
**Solution**: 
- Used GitHub Actions for Docker builds (runs on cloud runners)
- Created docker-compose files for documentation purposes
- Successfully deployed to Azure which handles containerization

### Challenge 2: Azure Permissions
**Problem**: Student Azure account had limited permissions (couldn't create service principals, restart apps, view logs)  
**Solution**:
- Used Azure Container Registry admin credentials instead of service principals
- Used Azure Portal UI for manual operations (restart, configuration)
- Configured managed identity with AcrPull role for secure ACR access
- Simplified CD workflow to only build and push (Azure handles deployment via Deployment Center)

### Challenge 3: Container Port Configuration
**Problem**: Azure Web App showed ASP.NET default page instead of Flask app  
**Solution**:
- Set `WEBSITES_PORT=8000` environment variable in Azure Portal
- Configured Deployment Center to use Azure Container Registry
- Enabled continuous deployment to auto-pull latest images
- Manually restarted Web App to apply changes

### Challenge 4: GitHub Actions YAML Syntax
**Problem**: Initial CD workflow had syntax errors in conditional expressions  
**Solution**:
- Removed problematic `if` conditions comparing secrets
- Simplified workflow to use one authentication method consistently
- Tested YAML syntax incrementally with small commits

### Challenge 5: Test Coverage Calculation
**Problem**: Needed to achieve 70% coverage  
**Solution**:
- Created comprehensive test suite covering all major code paths
- Added integration tests for API endpoints
- Tested file uploads and customization features
- Achieved 72% coverage, exceeding requirement

---

## Conclusion

This project successfully implements a complete DevOps pipeline for the Typo Blog application. All Assignment 2 requirements have been met:

✅ **Code Quality**: Linting with Ruff, zero errors  
✅ **Testing**: 72% coverage with comprehensive test suite  
✅ **CI Pipeline**: Automated checks on every push/PR  
✅ **CD Pipeline**: Automated deployment to Azure  
✅ **Containerization**: Production-ready Docker setup  
✅ **Cloud Deployment**: Live on Azure Web App  
✅ **Monitoring**: Prometheus metrics with Grafana dashboards  
✅ **Documentation**: Complete setup and usage instructions  

The application is successfully deployed and accessible at:
**https://sof-typo-webapp-2004.azurewebsites.net**

---

## References

- GitHub Repository: https://github.com/sofiasanjose/typo-blog-app
- Flask Documentation: https://flask.palletsprojects.com/
- Pytest Documentation: https://docs.pytest.org/
- Docker Documentation: https://docs.docker.com/
- Azure Web Apps: https://learn.microsoft.com/en-us/azure/app-service/
- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/
- GitHub Actions: https://docs.github.com/en/actions
- Ruff Linter: https://docs.astral.sh/ruff/
