# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Restaurant Scorer is a minimal restaurant-scoring webapp built with FastAPI, SQLite, HTMX, and Tailwind CSS. It allows users to score restaurants on taste, experience, and value, with a mood-adjusted scoring algorithm: `(taste + experience + value) / mood`.

## Essential Commands

### Development Setup

#### Python Virtual Environment

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server with auto-reload
uvicorn app.main:app --reload --port 8000
```

#### Docker Development

```bash
# Build and run with Docker
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Testing API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get entries as JSON
curl http://localhost:8000/entries

# Test form submission
curl -X POST http://localhost:8000/submit \
  -F "restaurant_name=Test Restaurant" \
  -F "gmaps_link=https://maps.google.com/test" \
  -F "date_visited=2024-01-15" \
  -F "mood=1.0" \
  -F "taste=8" \
  -F "experience=7" \
  -F "value=9" \
  -F "notes=Test submission"
```

## Architecture Overview

### Project Structure

```
restaurant-database/
├── app/                         # Main application package
│   ├── __init__.py             # Python package marker
│   ├── main.py                 # FastAPI application & endpoints
│   ├── models.py               # SQLModel data models
│   └── templates/              # Jinja2 HTML templates
│       └── index.html          # Main form interface
├── data/                       # Database storage (auto-created)
│   └── food.db                 # SQLite database file
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
└── docker-compose.yml          # Multi-container orchestration
```

### Core Components

1. **FastAPI Application (`app/main.py`)**: 
   - Defines all API endpoints and application logic
   - Handles form submissions and image processing
   - Manages database operations
   - Key endpoints: `/`, `/submit`, `/entries`, `/history`, `/health`

2. **Data Model (`app/models.py`)**: 
   - Defines `ScoreEntry` SQLModel for database schema
   - Fields include restaurant details, scores, and image paths

3. **Frontend (`app/templates/index.html`)**:
   - HTMX-powered form for submitting restaurant scores
   - Real-time score calculation with JavaScript
   - Image upload and preview functionality
   - History view with sort capabilities

4. **Database**:
   - SQLite database stored in `data/food.db`
   - Created automatically on first run
   - File-based persistence through Docker volume

### Data Flow

1. **Form Submission**:
   ```
   User fills form → HTMX POST → FastAPI validation → Score calculation → SQLite storage → Success response
   ```

2. **Score Calculation**:
   ```
   Final Score = (Taste + Experience + Value) ÷ Mood
   ```

3. **Database Operations**:
   ```
   SQLModel → SQLAlchemy → SQLite
   ```

## Key Technical Decisions

1. **FastAPI & SQLModel**: Modern, type-safe Python web framework with automatic OpenAPI docs
2. **SQLite**: Zero-configuration, single-file database suitable for low-scale usage
3. **HTMX**: Dynamic form interactions without complex JavaScript
4. **Tailwind CSS**: Utility-first CSS for responsive design without writing custom CSS
5. **Docker**: Containerized deployment for easy setup and portability
6. **Image Handling**: Built-in support for image uploads, including HEIC/HEIF format

## Working With The Code

When modifying this codebase, keep these points in mind:

1. **Database Schema**: Any changes to `models.py` will affect the database schema
2. **Image Processing**: The app includes special handling for HEIC/HEIF image formats
3. **Frontend Interactions**: Most UI updates use HTMX for dynamic HTML without page refreshes
4. **Real-time Calculations**: JavaScript functions handle live score calculations and form feedback
5. **Mobile-First Design**: The UI is designed to work well on mobile devices

## Deployment Notes

The application is designed to be deployed using:
- Docker container
- Cloudflare Tunnel for secure HTTPS access
- Cloudflare Zero Trust authentication
- Local mini-PC or VPS hosting