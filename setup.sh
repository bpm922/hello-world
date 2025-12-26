#!/bin/bash
# Setup script for OSINT Framework

set -e

echo "========================================="
echo "OSINT Framework Setup"
echo "========================================="
echo

# Check Python version
echo "Checking Python version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo
echo "Installing dependencies..."
pip install -r requirements.txt

# Verify installation
echo
echo "Verifying installation..."
python -c "from core import OSINTEngine; from plugins import discover_plugins; print('✓ Core modules loaded successfully')"

echo
echo "========================================="
echo "✓ Setup completed successfully!"
echo "========================================="
echo
echo "To start using the framework:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo
echo "  2. Run the main application:"
echo "     python main.py"
echo
echo "  3. Or try the examples:"
echo "     python example_usage.py"
echo
echo "  4. Run tests:"
echo "     python test_framework.py"
echo
