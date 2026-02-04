# XLSForm AI Installation Script (Windows PowerShell)

Write-Host "🚀 Installing XLSForm AI CLI..." -ForegroundColor Cyan

# Check if uv is installed
$uvInstalled = $false
try {
    $uvVersion = uv --version 2>$null
    if ($uvVersion) {
        $uvInstalled = $true
        Write-Host "✓ uv is installed (version $uvVersion)" -ForegroundColor Green
    }
} catch {
    # uv not found
}

if (-not $uvInstalled) {
    Write-Host "⚠️  uv is not installed. Installing uv..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex
}

# Install the CLI
Write-Host "📦 Installing xlsform-ai-cli..." -ForegroundColor Cyan
uv tool install xlsform-ai-cli --from git+https://github.com/yourusername/xlsform-ai.git

# Verify installation
Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Verify installation:"
Write-Host "  xlsform-ai check" -ForegroundColor Cyan
Write-Host ""
Write-Host "Create a new project:"
Write-Host "  xlsform-ai init my-survey" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more information:"
Write-Host "  xlsform-ai info" -ForegroundColor Cyan
Write-Host "  https://github.com/yourusername/xlsform-ai" -ForegroundColor Cyan
