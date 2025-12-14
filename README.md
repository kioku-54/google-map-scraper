# Google Maps Scraper

A Python-based scraper for Google Maps that extracts places information (POIs) using browser automation. The system processes search queries by "place categories" and H3 grid, extracts place details, and stores results in PostgreSQL.


## Tech Stack

### Core Dependencies
- **Python 3.11+** - Programming language
- **Playwright** - Browser automation
- **SQLAlchemy + asyncpg** - Async database ORM
- **H3** - Geospatial indexing
- **BeautifulSoup4 + lxml** - HTML parsing
- **Pydantic V2** - Data validation
- **FastAPI + Uvicorn** - HTTP API server
- **Redis** - Queue management
- **Cryptography** - Encryption utilities
- **Alembic** - Database migrations

### Development Dependencies
- **pytest** - Testing framework
- **pytest-asyncio** - Async testing support
- **pytest-mock** - Mocking utilities
- **black** - Code formatting
- **ruff** - Linting
- **mypy** - Type checking
- **diagrams** - Architecture diagram generation

## Project Structure

The project follows Clean Architecture with clear separation of concerns:

```
google-map-scraper/
├── src/
│   ├── config/              # Configuration module
│   ├── cmd/                 # Application entry points
│   │   └── server/          # Server entry point (main.py, api.py, worker.py)
│   └── internal/            # Internal application code
│       ├── constants/       # Constants
│       ├── external/        # External service integrations
│       │   └── google_map/  # Google Maps integration
│       ├── model/           # Data models
│       │   ├── dto/         # Data Transfer Objects
│       │   └── entity/      # Database entities
│       ├── services/        # Business logic services
│       ├── store/           # Data access layer
│       │   ├── database/    # Database connection
│       │   ├── google_map_store/      # Job queue & result storage
│       │   └── google_map_result_store/ # Duplicate checking
│       ├── usecase/         # Use cases / Application logic
│       │   └── gmapscraper/ # Scraper orchestration
│       └── utils/           # Utility functions
├── tests/                   # Tests (alternative location)
│   ├── unit/
│   └── integration/
├── docs/                    # Documentation
├── alembic/                 # Database migrations
└── planning/                # Planning documents
```

## Prerequisites

- **Python 3.11+**
- **uv** - Modern Python package manager ([Installation Guide](https://github.com/astral-sh/uv))
- **PostgreSQL 14+** with PostGIS extension
- **Redis 6+**
- **Playwright browsers** (installed automatically)

## Setup Instructions

### 1. Install UV

If you haven't installed `uv` yet:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Setup Project

```bash
# Clone the repository
git clone <repository-url>
cd google-map-scraper

# Initialize project and install dependencies
uv sync

# Install Playwright browsers
uv run playwright install
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# - Database connection details
# - Redis connection details
# - API settings
# - Scraper settings
```

### 4. Database Setup

```bash
# Create PostgreSQL database with PostGIS
createdb gmaps_scraper
psql gmaps_scraper -c "CREATE EXTENSION postgis;"

# Run migrations (after Phase 2)
# uv run alembic upgrade head
```

### 5. Redis Setup

```bash
# Start Redis (if not running)
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:latest
```

## Development Workflow

### Running the Application

```bash
# Run the API server
uv run python -m src.cmd.server.main

# Or run with uvicorn directly
uv run uvicorn src.cmd.server.api:app --reload
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit

# Run integration tests only
uv run pytest tests/integration

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
uv run black src tests

# Lint code
uv run ruff check src tests

# Type checking
uv run mypy src
```

### Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```
