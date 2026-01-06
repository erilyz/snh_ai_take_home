# SNH AI - HTTP Server Coding Challenge

Production-ready HTTP API for managing hierarchical tree data structures. Built with FastAPI, designed for simplicity, cost-effectiveness, and cloud portability.

> 📐 **Detailed architecture documentation**: See `docs/ARCHITECTURE.md`

## Architecture

**Core Stack:**
- **FastAPI** - Modern Python web framework with automatic OpenAPI docs
- **Cloud Storage** - JSON-based persistence (GCS/S3/Local) for cost-effective POC
- **Structured Logging** - JSON logs for observability
- **Graceful Error Handling** - Resilient design with health checks

**Design Philosophy:**
- Simple, maintainable codebase
- Storage abstraction allows seamless migration from local → GCS → S3
- In-memory tree operations with atomic persistence
- Production patterns: health checks, structured logging, comprehensive tests

## Quick Start (Local Development)

### Prerequisites
- **Docker** (recommended) - [Install Docker](https://docs.docker.com/get-docker/)
- **OR Python 3.9+** and pip
- **Supported OS**: macOS, Ubuntu/Debian Linux, Windows 10/11

**Platform-specific setup:**
- **macOS**: `brew install python@3.11` (if needed)
- **Ubuntu/Debian**: `sudo apt install python3 python3-pip python3-venv`
- **Windows**: Download from [python.org](https://www.python.org/downloads/) or use WSL

### Setup

**Option 1: Docker (Recommended)**

```bash
# Clone the repository
git clone https://github.com/erilyz/snh_ai_take_home.git
cd snh_ai_take_home

# Build and run with Docker (with data persistence)
docker build -t tree-api .
docker run -p 8000:8000 -v $(pwd)/data:/app/data tree-api
```

**Option 2: Virtual Environment (Recommended for Development)**

```bash
# Clone the repository
git clone https://github.com/erilyz/snh_ai_take_home.git
cd snh_ai_take_home

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
./scripts/run.sh

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
.\scripts\run.ps1
```

**Option 3: System Python (Quick Test)**

```bash
# macOS/Linux
pip3 install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Run Tests

```bash
# With venv activated
pytest -v

# Or with Docker
docker run tree-api pytest -v
```

## API Endpoints

### GET /api/tree
Returns all trees with their hierarchical structure.

**Example Response:**
```json
[
  {
    "id": 1,
    "label": "root",
    "children": [
      {
        "id": 3,
        "label": "bear",
        "children": [
          {
            "id": 4,
            "label": "cat",
            "children": []
          }
        ]
      }
    ]
  }
]
```

> **Note**: IDs are auto-incremented sequentially. The example shows IDs 1, 3, 4 to illustrate that IDs persist even if intermediate nodes are deleted (though deletion is not currently implemented).

### POST /api/tree
Creates a new node and attaches it to a parent (or creates a new root).

**Request Body:**
```json
{
  "label": "new_node",
  "parent_id": 1  // Optional: omit to create new root
}
```

**Response:**
```json
{
  "id": 3,
  "label": "new_node",
  "parent_id": 1
}
```

## Configuration

Environment variables for different storage backends:

### Local (Default)
```bash
STORAGE_TYPE=local
STORAGE_PATH=data/trees.json  # Optional, default shown
LOG_LEVEL=INFO  # Optional: DEBUG, INFO, WARNING, ERROR
```

### Google Cloud Storage
```bash
STORAGE_TYPE=gcs
GCS_BUCKET_NAME=your-bucket-name
GCS_OBJECT_NAME=trees.json  # Optional
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### AWS S3
```bash
STORAGE_TYPE=s3
S3_BUCKET_NAME=your-bucket-name
S3_OBJECT_KEY=trees.json  # Optional
AWS_REGION=us-east-1  # Optional
# AWS credentials via standard AWS SDK methods (env vars, ~/.aws/credentials, IAM role)
```

## Production Deployment

### Infrastructure Setup

**Production Best Practices:**
- Terraform state should be managed by a **service account with minimal permissions**
- Infrastructure changes should be applied via **CI/CD pipelines** (not manually)
- Use remote state backends (GCS/S3) with state locking
- Implement proper approval workflows for production changes

The Terraform configurations provided define the resources needed for production deployment. The application works perfectly with local storage for development and testing.

#### GCP Deployment
```bash
cd terraform/gcp
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project details
terraform init
terraform plan
terraform apply
```

**Creates:**
- GCS bucket with versioning
- Service account with minimal permissions
- IAM bindings

#### AWS Deployment
```bash
cd terraform/aws
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your settings
terraform init
terraform plan
terraform apply
```

**Creates:**
- S3 bucket with versioning and lifecycle policies
- IAM role and policy
- Instance profile for EC2

### Deployment Options

**Option 1: Cloud Run (GCP)**
```bash
gcloud run deploy tree-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars STORAGE_TYPE=gcs,GCS_BUCKET_NAME=<bucket-name>
```

**Option 2: AWS ECS/Fargate**
- Build Docker image
- Push to ECR
- Deploy to ECS with task role attached

### CI/CD Considerations

**Recommended Pipeline:**
1. **Build Stage**
   - Install dependencies
   - Run linters (black, flake8, mypy)
   - Run tests with coverage

2. **Deploy Stage**
   - Build container image
   - Push to registry (GCR/ECR)
   - Deploy to Cloud Run/ECS
   - Run smoke tests

**Tools:** GitHub Actions, GitLab CI, or Cloud Build

**Example GitHub Actions workflow structure:**
```yaml
- Checkout code
- Setup Python
- Install dependencies
- Run pytest
- Build Docker image (if tests pass)
- Deploy to staging/production
```

## Cost Estimates (Monthly)

### Development/POC
- **GCP**: ~$0.50-2/month
  - Cloud Storage: $0.02/GB
  - Cloud Run: Free tier covers POC usage

- **AWS**: ~$0.50-2/month
  - S3: $0.023/GB
  - ECS Fargate: ~$15/month (0.25 vCPU, 0.5GB RAM)

### Production (Low Traffic: <10K requests/day)
- **GCP**: ~$20-30/month
  - Cloud Storage: $1-2
  - Cloud Run: $15-25 (based on usage)

- **AWS**: ~$25-35/month
  - S3: $1-2
  - ECS Fargate: $20-30

**Cost Optimization:**
- Use Cloud Run/Lambda for variable traffic (pay per request)
- Storage costs scale with data size (minimal for tree structures)
- Enable lifecycle policies to manage old versions

## Observability & Monitoring

**Built-in:**
- Structured JSON logging for easy parsing
- Health check endpoint (`/health`)
- Automatic OpenAPI documentation

**Recommended Production Stack:**
- **Metrics & Dashboards**: Grafana + Prometheus
  - Request rates, latency percentiles, error rates
  - Custom dashboards for tree operations
  - Cost-effective and cloud-agnostic

- **Logging**: Minimal cloud logging to control costs
  - GCP: Cloud Logging with log exclusion filters (errors only)
  - AWS: CloudWatch Logs with retention policies (7-14 days)
  - Consider log aggregation to Grafana Loki for cost savings

- **Tracing**: OpenTelemetry (optional, for complex debugging)
- **Alerting**: Grafana alerts on health check failures, error rate spikes

## Edge Cases & Error Handling

**Handled Gracefully:**
- Parent node not found → 404 with clear message
- Invalid JSON in storage → Logged error, returns 500
- Storage unavailable → Health check fails (503), API remains responsive
- Corrupted data file → Logged error with details
- Empty label → 422 validation error

**Resilience:**
- Atomic writes prevent data corruption
- Versioning in cloud storage allows rollback
- Health checks enable load balancer to route around unhealthy instances

## Future Enhancements

**When scaling beyond POC:**
1. **Database Migration**: Move from JSON storage to PostgreSQL/Cloud SQL
2. **Caching**: Add Redis for frequently accessed trees
3. **Authentication**: Add API keys or OAuth2
4. **Rate Limiting**: Prevent abuse
5. **Pagination**: For large tree lists
6. **WebSocket Support**: Real-time tree updates

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & endpoints
│   ├── models.py            # Pydantic models
│   ├── tree_manager.py      # Tree operations logic
│   ├── storage.py           # Storage abstraction (Local/GCS/S3)
│   └── logging_config.py    # Structured logging setup
├── tests/
│   ├── test_api.py          # API endpoint tests
│   ├── test_tree_manager.py # Tree logic tests
│   └── test_storage.py      # Storage backend tests
├── terraform/
│   ├── gcp/                 # GCP infrastructure
│   └── aws/                 # AWS infrastructure
├── docs/                    # Additional documentation
│   ├── ARCHITECTURE.md      # System design & diagrams
│   ├── PLATFORM_SUPPORT.md  # OS-specific guides
│   ├── CODE_QUALITY_REVIEW.md # Quality assessment
│   ├── DEVELOPMENT_NOTES.md # Developer guidelines
│   └── SUBMISSION_SUMMARY.md # Project summary
├── scripts/                 # Utility scripts
│   ├── run.sh              # macOS/Linux startup
│   ├── run.ps1             # Windows startup
│   ├── example_usage.py    # API usage examples
│   └── README.md           # Script documentation
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── QUICK_START.md          # Quick reference guide
└── README.md               # This file
```

## License

MIT

