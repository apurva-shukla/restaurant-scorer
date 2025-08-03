# Restaurant Scorer - Project Documentation

A minimal restaurant-scoring webapp built with FastAPI, SQLite, HTMX, and Tailwind CSS. This document provides a comprehensive overview of the project structure, implementation details, and technical decisions.

## 🏗️ Project Structure

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
├── .venv/                      # Python virtual environment
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Multi-container orchestration
├── .gitignore                  # Git ignore patterns
├── README.md                   # Quick start guide
├── plan.md                     # Original implementation plan
└── project.md                  # This documentation file
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** (0.104.1) - Modern Python web framework
- **SQLModel** (0.0.14) - Type-safe database modeling
- **SQLite** - Embedded database (zero-config)
- **Uvicorn** (0.24.0) - ASGI server with auto-reload
- **Jinja2** (3.1.2) - Template engine

### Frontend
- **HTMX** (1.9.10) - Dynamic HTML without build steps
- **Tailwind CSS** (via CDN) - Utility-first CSS framework
- **Vanilla JavaScript** - Real-time score calculation

### Deployment
- **Docker** - Containerization
- **Docker Compose** - Local development orchestration

## 📁 File Details

### `app/main.py` - FastAPI Application
The core application file containing:

**Database Setup**
```python
DATABASE_URL = "sqlite:///data/food.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

**API Endpoints**
- `GET /` - Serves the HTML form interface
- `POST /submit` - Processes form submissions and saves to database
- `GET /entries` - JSON API for retrieving restaurant scores
- `GET /health` - Health check endpoint

**Key Features**
- Automatic database table creation on startup
- Dependency injection for database sessions
- Form data validation and processing
- Real-time final score calculation: `(taste + experience + value) / mood`
- HTMX-compatible responses with success feedback

### `app/models.py` - Data Model
SQLModel-based data structure:

```python
class ScoreEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_name: str
    gmaps_link: str
    date_visited: date
    mood: float = 1.0              # 0.9-1.1 range
    taste: int                     # 0-10 scale
    experience: int                # 0-10 scale
    value: int                     # 0-10 scale
    notes: Optional[str] = None
    final_score: float             # Computed score
```

**Design Decisions**
- Auto-incrementing primary key for unique identification
- Required fields for core scoring data
- Optional notes field for additional context
- Float precision for mood adjustments and final scores

### `app/templates/index.html` - User Interface
A single-page form interface featuring:

**Modern UI Components**
- Responsive design with Tailwind CSS utilities
- Form validation with HTML5 input types
- Interactive mood slider with live value display
- Real-time final score calculation
- Success feedback via HTMX responses

**JavaScript Functionality**
```javascript
function updateFinalScore() {
    const taste = parseInt(document.getElementById('taste').value) || 0;
    const experience = parseInt(document.getElementById('experience').value) || 0;
    const value = parseInt(document.getElementById('value').value) || 0;
    const mood = parseFloat(document.getElementById('mood').value) || 1.0;
    
    const finalScore = (taste + experience + value) / mood;
    document.getElementById('final-score').textContent = finalScore.toFixed(2);
}
```

**HTMX Integration**
- `hx-post="/submit"` for form submission
- `hx-target="#response"` for dynamic feedback
- No page refresh required for form submissions

### `requirements.txt` - Dependencies
Carefully selected minimal dependencies:

```
fastapi==0.104.1           # Web framework
uvicorn[standard]==0.24.0  # ASGI server with extras
sqlmodel==0.0.14           # Database ORM
jinja2==3.1.2              # Template engine
python-multipart==0.0.6    # Form data parsing
python-dateutil==2.8.2     # Date handling utilities
```

### `Dockerfile` - Container Configuration
Multi-stage optimized container:

```dockerfile
FROM python:3.11-slim      # Lightweight Python base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /data         # SQLite storage directory
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `docker-compose.yml` - Development Environment
Local development setup:

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data         # Database persistence
    restart: unless-stopped
    environment:
      - PYTHONPATH=/app
```

## 🔄 Data Flow

### 1. Form Submission Flow
```
User fills form → HTMX POST → FastAPI validation → Score calculation → SQLite storage → Success response
```

### 2. Score Calculation
```
Final Score = (Taste + Experience + Value) ÷ Mood
```
- **Taste, Experience, Value**: 0-10 integer scales
- **Mood**: 0.9-1.1 float (bad mood decreases score, good mood increases it)
- **Result**: Precise float value displayed to 2 decimal places

### 3. Database Operations
```
SQLModel → SQLAlchemy → SQLite
```
- Automatic table creation via SQLModel.metadata.create_all()
- Session-based database operations with proper cleanup
- Type-safe queries using SQLModel's select() interface

## 🎯 Key Features

### Real-time Interactivity
- **Live Score Updates**: JavaScript calculates final score as user types
- **Mood Visualization**: Slider with descriptive labels and live value display
- **Form Validation**: HTML5 validation with required fields and input constraints

### Mobile-First Design
- **Responsive Layout**: Works seamlessly on phones and tablets
- **Touch-Friendly**: Large touch targets and proper spacing
- **Fast Loading**: CDN-delivered CSS/JS with minimal overhead

### Developer Experience
- **Auto-reload**: Uvicorn watches for file changes during development
- **Type Safety**: SQLModel provides compile-time type checking
- **API Documentation**: FastAPI auto-generates OpenAPI docs at `/docs`

### Production Ready
- **Health Checks**: `/health` endpoint for monitoring
- **Error Handling**: Proper HTTP status codes and error responses
- **Data Persistence**: SQLite file-based storage with volume mounting
- **Container Support**: Docker and Docker Compose configuration

## 🔌 API Endpoints

### `GET /`
**Purpose**: Serve the main form interface  
**Response**: HTML page with embedded CSS/JS  
**Content-Type**: `text/html`

### `POST /submit`
**Purpose**: Process restaurant score submissions  
**Input**: Form data (multipart/form-data)  
**Processing**: Validates input, calculates final score, saves to database  
**Response**: HTMX-compatible HTML fragment with success message

### `GET /entries`
**Purpose**: Retrieve restaurant scores as JSON  
**Query Parameters**: `limit` (default: 100)  
**Response**: Array of ScoreEntry objects  
**Use Case**: API consumption by external apps (e.g., Next.js blog)

### `GET /health`
**Purpose**: Health check for monitoring  
**Response**: `{"status": "healthy"}`  
**Use Case**: Load balancer health checks, uptime monitoring

## 🚀 Deployment Architecture

### Local Development
```
Browser → http://localhost:8000 → FastAPI → SQLite
```

### Production (Planned)
```
Browser → HTTPS → Cloudflare Zero Trust → Cloudflare Tunnel → Mini-PC → Docker → FastAPI → SQLite
```

**Security Layers**
1. **Cloudflare Zero Trust**: Email/OTP authentication
2. **Cloudflare Tunnel**: No open firewall ports required
3. **Docker Isolation**: Containerized application environment

## 📊 Database Schema

### `scoreentry` Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `restaurant_name` | TEXT | NOT NULL | Restaurant name |
| `gmaps_link` | TEXT | NOT NULL | Google Maps URL |
| `date_visited` | DATE | NOT NULL | Visit date (YYYY-MM-DD) |
| `mood` | REAL | NOT NULL, DEFAULT 1.0 | Mood factor (0.9-1.1) |
| `taste` | INTEGER | NOT NULL | Taste score (0-10) |
| `experience` | INTEGER | NOT NULL | Experience score (0-10) |
| `value` | INTEGER | NOT NULL | Value score (0-10) |
| `notes` | TEXT | NULLABLE | Optional notes |
| `final_score` | REAL | NOT NULL | Calculated final score |

### Sample Data
```json
{
  "id": 1,
  "restaurant_name": "Best Pizza Place",
  "gmaps_link": "https://maps.google.com/...",
  "date_visited": "2024-01-15",
  "mood": 1.0,
  "taste": 8,
  "experience": 7,
  "value": 9,
  "notes": "Great thin crust, friendly service",
  "final_score": 24.0
}
```

## 🔧 Development Commands

### Local Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Docker Development
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Testing Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Get entries
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

## 🎨 UI/UX Design Principles

### Visual Hierarchy
- **Large, clear headings** establish page purpose
- **Color coding** for different UI states (blue for primary, green for success)
- **Progressive disclosure** with collapsible sections

### Interaction Design
- **Immediate feedback** on all user actions
- **Clear affordances** (buttons look clickable, sliders are draggable)
- **Logical tab order** for keyboard navigation

### Accessibility
- **Semantic HTML** with proper labels and form structure
- **High contrast** color scheme for readability
- **Keyboard navigation** support throughout the interface

## 🔮 Future Enhancements

### Planned Features (from original plan)
1. **Read-only integration** with Next.js blog via `/entries` API
2. **Cloudflare Tunnel** deployment for secure remote access
3. **Automated backups** to cloud storage (Backblaze B2)
4. **Data export** functionality for backup/migration

### Potential Improvements
- **Search and filtering** of restaurant entries
- **Data visualization** (charts, trends over time)
- **Photo uploads** for restaurant images
- **Rating categories** expansion (ambiance, service, etc.)
- **Social features** (sharing scores, recommendations)

## 📈 Performance Characteristics

### Database Performance
- **SQLite**: Handles 200 rows easily, scales to thousands
- **Single file**: Simple backup and migration
- **No connection pooling**: Adequate for 2-user scale

### Web Performance
- **CDN delivery**: Tailwind and HTMX served from fast CDNs
- **Minimal JavaScript**: Only essential client-side code
- **Efficient templates**: Jinja2 template compilation and caching

### Scaling Considerations
- **Current scale**: Designed for 2 users, ~200 entries over 2 years
- **Horizontal scaling**: Would require PostgreSQL and load balancer
- **Vertical scaling**: Current architecture scales to hundreds of users

## 🛡️ Security Considerations

### Input Validation
- **HTML5 validation**: Client-side validation for immediate feedback
- **Pydantic validation**: Server-side validation via FastAPI/SQLModel
- **SQL injection prevention**: SQLModel/SQLAlchemy parameterized queries

### Authentication (Planned)
- **Cloudflare Zero Trust**: Email-based authentication
- **No local auth**: Delegated to Cloudflare for simplicity

### Data Protection
- **Local storage**: Database stored locally on trusted hardware
- **No sensitive data**: Restaurant scores are not personally sensitive
- **Backup encryption**: Planned for cloud backup storage

---

This documentation provides a complete technical overview of the Restaurant Scorer project. For quick start instructions, see [README.md](README.md). For the original implementation plan, see [plan.md](plan.md). 