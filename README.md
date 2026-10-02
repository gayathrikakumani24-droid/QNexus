# Qnexus - AI-Powered JEE Main PYQ Intelligence Platform

Qnexus is an AI-powered Previous Year Questions (PYQ) platform for JEE Main preparation. It provides shift-wise paper indexing, semantic PYQ search, interactive practice, weakness detection, and AI tutoring.

## Project Structure

- `backend/`: FastAPI application server, PyMongo, Pinecone Cloud client, and Groq SDK.
- `frontend/`: React + Vite + Tailwind CSS single page application.
- `data/`: Raw and processed dataset files.
- `scripts/`: Operational and maintenance scripts.

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
# Activate venv
pip install -r requirements.txt
python app/main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
