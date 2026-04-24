# Bug Report AI

A monorepo web application that uses AI to analyze screenshots and generate structured bug reports.

## Structure

- **frontend/** - React + Vite frontend application
- **backend/** - FastAPI backend application

## Getting Started

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```