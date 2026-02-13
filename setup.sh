#!/bin/bash
# WordPress Monitor - Setup Script (Linux/Mac)

echo "========================================"
echo "  WordPress Monitor - Setup"
echo "========================================"
echo ""

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "Python not found! Please install Python 3.8+"
    exit 1
fi

echo "Found: $($PYTHON --version)"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo ""
echo "Creating directories..."
mkdir -p logs reports screenshots data data/baselines

# Check config
echo ""
echo "Checking configuration..."
if [ -f "config/config.yaml" ]; then
    echo "Configuration file exists"
    echo ""
    echo "IMPORTANT: Edit config/config.yaml to set your website URL!"
else
    echo "Configuration file not found!"
fi

# Create .env from example
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Created .env file from template"
fi

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit config/config.yaml with your website URL"
echo "2. Edit .env with your email/Slack credentials"
echo "3. Run: python cli.py check --url https://your-site.com"
echo ""
echo "Or run the interactive setup:"
echo "  python cli.py init"
echo ""
