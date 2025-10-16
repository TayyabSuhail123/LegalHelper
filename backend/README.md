# ContractCopilot Backend

FastAPI-based backend service for ContractCopilot - AI-Powered Legal Document Risk Scanner.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- UV (recommended) or pip
- Docker (optional)

### Local Development with UV (Recommended)

1. **Install UV** (if not already installed):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or with pip
   pip install uv
   ```

2. **Create virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

3. **Or install development dependencies:**
   ```bash
   uv pip install -e ".[dev]"
   ```

4. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application:**
   ```bash
   # With UV (recommended)
   uv run --with fastapi --with "uvicorn[standard]" --with pydantic-settings uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Alternative: Traditional Setup

1. **Setup virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application:**
   - API: http://localhost:8000
   - Health Check: http://localhost:8000/api/v1/health
   - API Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Development

#### Quick Start with Docker Compose (from project root)
```bash
# Start all services (backend, frontend, redis, nginx)
docker-compose up --build

# Start only backend service
docker-compose up backend

# View logs
docker-compose logs -f backend
```

#### Build and Run Backend Container Only
```bash
# Build the image
docker build -t contractcopilot-backend .

# Run the container
docker run -p 8000:8000 \
  -e DEBUG=true \
  -e ENVIRONMENT=development \
  contractcopilot-backend

# Run with environment file
docker run -p 8000:8000 --env-file .env contractcopilot-backend
```

#### Production Build
```bash
# Build production image
docker build -f Dockerfile.prod -t contractcopilot-backend:prod .

# Run production container
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e OPENAI_API_KEY=your_key_here \
  contractcopilot-backend:prod
```

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── api/           # API route handlers
│   │   ├── __init__.py
│   │   └── health.py  # Health check endpoints
│   ├── core/          # Core functionality
│   │   ├── __init__.py
│   │   └── config.py  # Configuration settings
│   ├── models/        # Pydantic models
│   │   ├── __init__.py
│   │   └── responses.py  # Response models
│   └── __init__.py
├── tests/             # Test files
│   ├── __init__.py
│   ├── conftest.py   # Test configuration
│   └── test_health.py # Health endpoint tests
├── main.py           # FastAPI application entry point
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container configuration
├── .env.example     # Environment template
└── README.md        # This file
```

## 🔧 API Endpoints

### Health Check
- **GET** `/api/v1/health` - Basic health check
- **GET** `/api/v1/health/detailed` - Detailed system information

### Documentation
- **GET** `/docs` - Swagger UI documentation
- **GET** `/redoc` - ReDoc documentation
- **GET** `/openapi.json` - OpenAPI specification

## 🧪 Testing

Run tests with pytest:

```bash
# With UV (recommended)
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_health.py -v

# Traditional approach
pytest
pytest --cov=app --cov-report=html
```

## 🎨 Code Quality

```bash
# Format code with black
uv run black .

# Sort imports with isort
uv run isort .

# Lint with flake8
uv run flake8 .

# Type checking with mypy
uv run mypy app/

# Or install dev dependencies and run directly
uv pip install -e ".[dev]"
black .
isort .
flake8 .
mypy app/
```

## ⚙️ Configuration

Configuration is managed through environment variables and the `.env` file:

```env
# Application Settings
APP_NAME=ContractCopilot
DEBUG=true
ENVIRONMENT=development

# Server Settings  
HOST=0.0.0.0
PORT=8000

# API Settings
API_V1_PREFIX=/api/v1
```

## 🐳 Docker

### Build Image
```bash
docker build -t contractcopilot-backend .
```

### Run Container
```bash
docker run -p 8000:8000 -e DEBUG=true contractcopilot-backend
```

### Health Check
The Docker image includes a health check that monitors the `/api/v1/health` endpoint.

## 🔄 Development Workflow

1. **Make changes** to the code
2. **Run tests** to ensure functionality
3. **Test locally** with uvicorn
4. **Build Docker image** for containerized testing
5. **Update documentation** as needed

## 📊 Logging

The application uses Python's standard logging module. Logs include:
- Request/response information
- Error details
- Health check status
- Application startup/shutdown events

## 🔒 Security

- Non-root user in Docker container
- CORS middleware configured
- Input validation with Pydantic
- Environment-based configuration

## 🚦 Next Steps

This minimal backend provides:
- ✅ FastAPI application structure
- ✅ Health check endpoints
- ✅ Pydantic models
- ✅ Docker containerization
- ✅ Basic testing setup
- ✅ Configuration management

Future enhancements will include:
- File upload endpoints
- LLM integration with LangChain
- Contract analysis pipeline
- Langfuse observability
- Authentication and authorization
