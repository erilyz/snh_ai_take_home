# PowerShell script to run the Tree API locally on Windows
# Supports: Windows 10/11 with PowerShell 5.1+

$ErrorActionPreference = "Stop"

Write-Host "🌳 Tree Management API - Startup Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Function to print status
function Write-Status {
    param($success, $message)
    if ($success) {
        Write-Host "✓ " -ForegroundColor Green -NoNewline
        Write-Host $message
    } else {
        Write-Host "✗ " -ForegroundColor Red -NoNewline
        Write-Host $message
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..."
Write-Host ""

$missingDeps = $false

# Check Python
if (Test-CommandExists python) {
    $pythonVersion = (python --version 2>&1) -replace "Python ", ""
    Write-Status $true "Python found (version $pythonVersion)"
    $pythonCmd = "python"
} elseif (Test-CommandExists python3) {
    $pythonVersion = (python3 --version 2>&1) -replace "Python ", ""
    Write-Status $true "Python 3 found (version $pythonVersion)"
    $pythonCmd = "python3"
} else {
    Write-Status $false "Python not found"
    Write-Host "  Install: https://www.python.org/downloads/" -ForegroundColor Yellow
    $missingDeps = $true
}

# Check pip
if (Test-CommandExists pip) {
    Write-Status $true "pip found"
    $pipCmd = "pip"
} elseif (Test-CommandExists pip3) {
    Write-Status $true "pip3 found"
    $pipCmd = "pip3"
} else {
    Write-Status $false "pip not found"
    Write-Host "  Install: $pythonCmd -m ensurepip --upgrade" -ForegroundColor Yellow
    $missingDeps = $true
}

# Check curl (optional)
if (Test-CommandExists curl) {
    Write-Status $true "curl found (for testing)"
} else {
    Write-Status $false "curl not found (optional, but recommended for testing)"
    Write-Host "  curl.exe is built into Windows 10/11. If missing, update Windows." -ForegroundColor Yellow
}

Write-Host ""

# Exit if missing required dependencies
if ($missingDeps) {
    Write-Host "Missing required dependencies. Please install them and try again." -ForegroundColor Red
    exit 1
}

Write-Host "All prerequisites met!" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    & $pythonCmd -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Install dependencies if needed
$fastApiInstalled = & pip show fastapi 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing dependencies..."
    & pip install -r requirements.txt
}

# Set default environment variables
if (-not $env:STORAGE_TYPE) { $env:STORAGE_TYPE = "local" }
if (-not $env:STORAGE_PATH) { $env:STORAGE_PATH = "data/trees.json" }
if (-not $env:LOG_LEVEL) { $env:LOG_LEVEL = "INFO" }

Write-Host ""
Write-Host "Configuration:"
Write-Host "  Storage Type: $env:STORAGE_TYPE"
Write-Host "  Storage Path: $env:STORAGE_PATH"
Write-Host "  Log Level: $env:LOG_LEVEL"
Write-Host ""
Write-Host "API will be available at:"
Write-Host "  - API: http://localhost:8000"
Write-Host "  - Docs: http://localhost:8000/docs"
Write-Host "  - Health: http://localhost:8000/health"
Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host ""

# Run the server
& uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

