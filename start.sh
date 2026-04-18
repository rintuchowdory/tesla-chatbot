#!/bin/bash
cd ~/tesla-chatbot

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "========================================"
echo "  Tesla AI Chatbot starting on port 8000"
echo "  Open: http://localhost:8000"
echo "========================================"

python3 main.py
