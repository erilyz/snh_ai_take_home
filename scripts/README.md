# Scripts Directory

Utility scripts for the HTTP Server Coding Challenge.

## Available Scripts

### `run.sh` / `run.ps1` - Start Server
**macOS/Linux:**
```bash
./scripts/run.sh
```

**Windows:**
```powershell
.\scripts\run.ps1
```

Automatically sets up virtual environment, installs dependencies, and starts the server on port 8000.

---

### `example_usage.py` - API Examples
```bash
# Start server first
./scripts/run.sh

# In another terminal
python scripts/example_usage.py
```

Demonstrates creating nodes, retrieving trees, and error handling.

---

## Environment Variables

- `STORAGE_TYPE` - Storage backend: `local` (default), `gcs`, or `s3`
- `LOG_LEVEL` - Logging level: `INFO` (default), `DEBUG`, `WARNING`, `ERROR`
- `PORT` - Server port (default: 8000)

**Example:**
```bash
export STORAGE_TYPE=gcs
export GCS_BUCKET_NAME=my-bucket
./scripts/run.sh
```

---

## Troubleshooting

**Permission denied:**
```bash
chmod +x scripts/*.sh
```

**Port in use:**
```bash
export PORT=8001
./scripts/run.sh
```

**Python not found:**
- macOS: `brew install python@3.11`
- Ubuntu: `sudo apt install python3 python3-venv`
- Windows: Download from python.org
