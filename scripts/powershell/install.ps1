# XLSForm AI Installation Script (Windows PowerShell)

Write-Host "Installing XLSForm AI CLI..." -ForegroundColor Cyan
Write-Host "An open source project by ARCED International" -ForegroundColor Cyan
Write-Host ""

# Check if uv is installed
$uvInstalled = $false
try {
    $uvVersion = uv --version 2>$null
    if ($uvVersion) {
        $uvInstalled = $true
        Write-Host "uv is installed (version $uvVersion)" -ForegroundColor Green
    }
} catch {
    # uv not found
}

if (-not $uvInstalled) {
    Write-Host "uv is not installed. Installing uv..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex
}

# Install the CLI
Write-Host "Installing xlsform-ai-cli..." -ForegroundColor Cyan
uv tool install xlsform-ai-cli --from git+https://github.com/ARCED-International/xlsform-ai.git

# Install runtime dependencies for local `python scripts/...` workflows
Write-Host "Installing runtime dependencies for project scripts..." -ForegroundColor Cyan
$pythonInstalled = $false

try {
    python -m pip --version | Out-Null
    python -m pip install --disable-pip-version-check openpyxl pyxform pdfplumber python-docx deep-translator
    $pythonInstalled = $true
} catch {
    # try py launcher
}

if (-not $pythonInstalled) {
    try {
        py -3 -m pip --version | Out-Null
        py -3 -m pip install --disable-pip-version-check openpyxl pyxform pdfplumber python-docx deep-translator
        $pythonInstalled = $true
    } catch {
        # no usable python launcher
    }
}

if (-not $pythonInstalled) {
    Write-Host "Could not find python/py on PATH." -ForegroundColor Yellow
    Write-Host "Please install dependencies manually:" -ForegroundColor Yellow
    Write-Host "  python -m pip install openpyxl pyxform pdfplumber python-docx deep-translator" -ForegroundColor Yellow
}

# Verify installation
Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Verify installation:"
Write-Host "  xlsform-ai check" -ForegroundColor Cyan
Write-Host ""
Write-Host "Create a new project:"
Write-Host "  xlsform-ai init my-survey" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more information:"
Write-Host "  xlsform-ai info" -ForegroundColor Cyan
Write-Host "  https://github.com/ARCED-International/xlsform-ai" -ForegroundColor Cyan
Write-Host "  https://arced-international.com" -ForegroundColor Cyan
