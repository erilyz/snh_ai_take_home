# Quick Start Guide

## 30-Second Setup

**Docker (Recommended):**
```bash
# 1. Clone and navigate
git clone https://github.com/erilyz/snh_ai_take_home.git
cd snh_ai_take_home

# 2. Build and run with data persistence
docker build -t tree-api .
docker run -p 8000:8000 -v $(pwd)/data:/app/data tree-api

# 3. Test (in another terminal)
curl http://localhost:8000/health
# Expected: {"status":"healthy","storage":"available"}
```

**Virtual Environment:**
```bash
# 1. Clone and navigate
git clone https://github.com/erilyz/snh_ai_take_home.git
cd snh_ai_take_home

# 2. Setup (macOS/Linux)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# 2. Setup (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# 3. Run tests
pytest -v

# 4. Start server
./scripts/run.sh          # macOS/Linux
.\scripts\run.ps1         # Windows

# 5. Try the API (in another terminal)
python scripts/example_usage.py
```

## Essential Commands

### Development
```bash
# Run server with auto-reload
./scripts/run.sh

# Run tests
pytest -v

# Run tests with coverage
pytest --cov=app --cov-report=html

# Format code
black app/ tests/

# Type checking
mypy app/
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","storage":"available"}

# Get all trees (initially empty)
curl http://localhost:8000/api/tree
# Expected: []

# Create root node
curl -X POST http://localhost:8000/api/tree \
  -H "Content-Type: application/json" \
  -d '{"label":"root"}'
# Expected: {"id":1,"label":"root","children":[]}

# Create child node
curl -X POST http://localhost:8000/api/tree \
  -H "Content-Type: application/json" \
  -d '{"label":"child","parent_id":1}'
# Expected: {"id":2,"label":"child","parent_id":1}

# Get all trees (now with data)
curl http://localhost:8000/api/tree
# Expected: [{"id":1,"label":"root","children":[{"id":2,"label":"child","children":[]}]}]

# Interactive docs
open http://localhost:8000/docs
```

### Cloud Deployment

#### GCP
```bash
# Deploy to Cloud Run
gcloud run deploy tree-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars STORAGE_TYPE=gcs,GCS_BUCKET_NAME=your-bucket

# Setup infrastructure
cd terraform/gcp
terraform init
terraform apply
```

#### AWS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t tree-api .
docker tag tree-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/tree-api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/tree-api:latest

# Setup infrastructure
cd terraform/aws
terraform init
terraform apply
```

## Environment Variables

```bash
# Local development (default)
export STORAGE_TYPE=local
export STORAGE_PATH=data/trees.json

# Google Cloud Storage
export STORAGE_TYPE=gcs
export GCS_BUCKET_NAME=your-bucket-name
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# AWS S3
export STORAGE_TYPE=s3
export S3_BUCKET_NAME=your-bucket-name
export AWS_REGION=us-east-1
```

## Troubleshooting

### Server won't start
```bash
# Check Python version (need 3.9+)
python3 --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check logs
export LOG_LEVEL=DEBUG
./scripts/run.sh
```

### Tests failing
```bash
# Clean cache
rm -rf .pytest_cache __pycache__ app/__pycache__ tests/__pycache__

# Reinstall dev dependencies
pip install -r requirements-dev.txt

# Run specific test
pytest tests/test_api.py::test_health_check -v
```

### Storage issues
```bash
# Reset local storage
rm -rf data/

# Check permissions
ls -la data/

# Verify cloud credentials
gcloud auth list  # GCP
aws sts get-caller-identity  # AWS
```

## Project Files

- **README.md** - Complete documentation
- **QUICK_START.md** - This file
- **docs/** - Additional documentation
  - **ARCHITECTURE.md** - Design decisions and component details
- **scripts/** - Utility scripts
  - **run.sh** / **run.ps1** - Server startup scripts
  - **example_usage.py** - API usage examples
  - **README.md** - Script documentation

## Next Steps

1. **README.md** - Full documentation and deployment guides
2. **docs/ARCHITECTURE.md** - System design and architecture diagrams
3. **app/** - Application source code
4. **tests/** - Test suite (23 tests, 95%+ coverage)
5. **terraform/** - Infrastructure as code (GCP & AWS)

