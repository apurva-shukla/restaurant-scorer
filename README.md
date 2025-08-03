# Restaurant Scorer

A minimal restaurant-scoring webapp built with FastAPI, SQLite, HTMX, and Tailwind CSS.

## Features

- Simple web form to score restaurants on taste, experience, and value
- Mood-adjusted scoring algorithm: `(taste + experience + value) / mood`
- Real-time score calculation as you type
- SQLite database for data persistence
- JSON API endpoint for external consumption
- Mobile-responsive design with Tailwind CSS
- HTMX for dynamic form interactions

## Local Development

### Option 1: Python Virtual Environment

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. Open http://localhost:8000 in your browser

### Option 2: Docker

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Open http://localhost:8000 in your browser

## API Endpoints

- `GET /` - Main form interface
- `POST /submit` - Submit restaurant score (form data)
- `GET /entries` - List recent entries as JSON
- `GET /health` - Health check

## Database

The SQLite database (`data/food.db`) will be created automatically on first run.

## Data Model

Each restaurant entry includes:
- Restaurant name
- Google Maps link
- Date visited
- Mood factor (0.9-1.1)
- Taste score (0-10)
- Experience score (0-10)
- Value score (0-10)
- Optional notes
- Calculated final score

## Deployment

This app is designed to be deployed with:
- Docker container
- Cloudflare Tunnel for secure HTTPS access
- Cloudflare Zero Trust authentication
- Local mini-PC or VPS hosting

See `plan.md` for detailed deployment instructions. 