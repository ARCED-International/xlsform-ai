#!/bin/bash
# XLSForm AI Installation Script (Unix/Linux/macOS)

set -e

echo "🚀 Installing XLSForm AI CLI..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install the CLI
echo "📦 Installing xlsform-ai-cli..."
uv tool install xlsform-ai-cli --from git+https://github.com/yourusername/xlsform-ai.git

# Verify installation
echo ""
echo "✅ Installation complete!"
echo ""
echo "Verify installation:"
echo "  xlsform-ai check"
echo ""
echo "Create a new project:"
echo "  xlsform-ai init my-survey"
echo ""
echo "For more information:"
echo "  xlsform-ai info"
echo "  https://github.com/yourusername/xlsform-ai"
