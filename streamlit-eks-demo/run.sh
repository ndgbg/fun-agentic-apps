#!/bin/bash

echo "🚀 Starting .NET to EKS Deployment Demo"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Start Streamlit app
echo "🌐 Starting Streamlit demo..."
echo "📍 Demo will open at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the demo"
echo ""

python3 -m streamlit run eks_demo.py