#!/bin/bash
# XLSForm AI Installation Script (Unix/Linux/macOS)

set -e

echo "Installing XLSForm AI CLI..."
echo "An open source project by ARCED International"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install the CLI
echo "Installing xlsform-ai-cli..."
uv tool install xlsform-ai-cli --from git+https://github.com/ARCED-International/xlsform-ai.git

# Install runtime dependencies for local `python scripts/...` workflows
echo "Installing runtime dependencies for project scripts..."
if command -v python &> /dev/null; then
    python -m pip install --disable-pip-version-check openpyxl pyxform pdfplumber python-docx
elif command -v python3 &> /dev/null; then
    python3 -m pip install --disable-pip-version-check openpyxl pyxform pdfplumber python-docx
else
    echo "Could not find python/python3 on PATH."
    echo "Please install dependencies manually:"
    echo "  python -m pip install openpyxl pyxform pdfplumber python-docx"
fi

# Verify installation
echo ""
echo "Installation complete!"
echo ""
echo "Verify installation:"
echo "  xlsform-ai check"
echo ""
echo "Create a new project:"
echo "  xlsform-ai init my-survey"
echo ""
echo "For more information:"
echo "  xlsform-ai info"
echo "  https://github.com/ARCED-International/xlsform-ai"
echo "  https://arced-international.com"