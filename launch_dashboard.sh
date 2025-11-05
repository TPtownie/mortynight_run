#!/bin/bash

echo "🚀 Launching Morty Express Dashboard..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "⚠️  Streamlit not found. Installing requirements..."
    pip install -r requirements.txt
    echo ""
fi

echo "🌐 Opening dashboard at http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run morty_dashboard.py
