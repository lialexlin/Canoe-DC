#!/bin/bash

set -e

echo "🚀 Setting up Canoe PDF Summarizer development environment..."

# Update system packages
sudo apt-get update

# Install 1Password CLI
echo "📦 Installing 1Password CLI..."
curl -sS https://downloads.1password.com/linux/keys/1password.asc | sudo gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg
echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/amd64 stable main' | sudo tee /etc/apt/sources.list.d/1password.list
sudo apt-get update && sudo apt-get install -y 1password-cli

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies
echo "🔧 Installing development tools..."
pip install black flake8 pytest pytest-cov pre-commit

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/temp_pdfs
mkdir -p logs

# Set up pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
EOF

pre-commit install

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Environment files
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/settings.json
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Data files
data/
*.pdf
*.xlsx
*.csv

# OS
.DS_Store
Thumbs.db

# Temporary files
temp/
tmp/
EOF
fi

# Set up example environment file
if [ ! -f .env.example ]; then
    echo "📋 Creating .env.example..."
    cat > .env.example << EOF
# 1Password Configuration (optional - for fallback)
OP_VAULT=Personal

# Fallback Environment Variables (if 1Password unavailable)
# CANOE_CLIENT_ID=your_canoe_client_id
# CANOE_CLIENT_SECRET=your_canoe_client_secret
# CANOE_BASE_URL=https://api.canoesoftware.com
# ANTHROPIC_API_KEY=your_anthropic_api_key
# NOTION_TOKEN=your_notion_integration_token
# NOTION_DATABASE_ID=your_notion_database_id

# Application Settings
MAX_RETRIES=3
LOG_LEVEL=INFO
EOF
fi

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Sign in to 1Password CLI: op signin"
echo "2. Set up your 1Password items (see README.md)"
echo "3. Copy .env.example to .env and configure if needed"
echo "4. Run: python main.py"