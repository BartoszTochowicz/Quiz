# Technical Quiz App Template

A starter template for a technical Quiz app using [quizapi.io](https://quizapi.io/docs/1.0/overview), Flask backend, and React frontend.

## Structure

- **backend/** — Flask REST API (modular)
- **frontend/** — React app (with `pages` and `assets`)

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export QUIZ_API_KEY=your_quizapi_key_here
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Configuration

- Set your `QUIZ_API_KEY` as an environment variable for backend.

---

This template mirrors modularity and style from `Pokemon_Arena` repository.