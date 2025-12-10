#!/bin/bash

# Start FastAPI backend in background
uvicorn src.services.recsys_agentic.main:app --host 0.0.0.0 --port 8000 &

# Wait for backend to be ready
sleep 5

# Start Streamlit frontend on Railway's PORT
streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
