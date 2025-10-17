# ContractCopilot - AI-Powered Legal Document Risk Scanner

> A production-grade AI system that analyzes legal contracts to identify risky clauses and assess their severity using advanced LLMs.

## 🎯 Project Overview

ContractCopilot is an enterprise-ready legal document analysis platform that helps legal professionals quickly identify and assess risks in contracts. The system uses OpenAI's GPT-4 to analyze uploaded contracts (PDF, DOCX, or text) and provides structured risk reports with plain-language explanations.

## 🏗️ Architecture

This is a monorepo containing three main components:

- **`frontend/`** - React TypeScript application for contract upload and risk visualization
- **`backend/`** - Python FastAPI service for document processing and LLM analysis
- **`infra/`** - Terraform infrastructure as code for AWS deployment

## ⚡ Quick Start

### Prerequisites

- Node.js 18+ and npm (for frontend development)
- Python 3.11+
- Docker and Docker Compose (for backend services only)
- AWS CLI (for deployment)
- Terraform (for infrastructure)

### Development Setup

```bash
# Clone and setup
git clone <repo-url>
cd autoreviwer

# Backend setup with Docker Compose
docker-compose up -d backend redis

# Frontend setup (runs locally, not dockerized)
cd frontend
npm install
npm start

# Or start backend with UV directly
cd backend
uv venv
uv pip install -r requirements.txt
uv run --with fastapi --with "uvicorn[standard]" --with pydantic-settings uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Development

### Development Workflow

- **Backend API**: http://localhost:8000 (Docker containerized)
- **Frontend App**: http://localhost:3000 (runs locally with npm)
- **API Docs**: http://localhost:8000/docs
- **Redis**: http://localhost:6379 (Docker containerized)

### Note on Docker Setup

- The backend and Redis run in Docker containers for consistency
- The frontend runs locally for faster development iteration
- Use `docker-compose up -d` to start only the backend services
- Use `npm start` in the frontend directory for live reloading

## 🚀 Key Features

- **Multi-format Support**: PDF, DOCX, and plain text contracts
- **AI-Powered Analysis**: GPT-4 clause detection and risk assessment
- **Risk Classification**: Low/Medium/High severity levels
- **Plain Language**: Human-readable explanations of legal risks
- **Structured Reports**: JSON and PDF export capabilities
- **Production Ready**: Full observability, security, and deployment automation

## 📊 Risk Detection Categories

- Termination clauses
- Indemnification terms
- Intellectual Property rights
- Confidentiality obligations
- Arbitration and Jurisdiction
- Liability limitations
- Payment terms
- Data protection clauses

## 🛡️ Security & Compliance

- File validation and sanitization
- Rate limiting and input validation
- Secure secrets management
- LLM output guardrails
- GDPR/SOC2 compliance ready

## 📈 Observability

- Langfuse integration for LLM tracing
- Performance monitoring
- Error tracking and alerting
- Usage analytics

## 🏭 Deployment

The system is designed for cloud deployment on AWS using Terraform:

- **ECS Fargate** for containerized services
- **S3** for file storage
- **CloudFront** for CDN
- **Secrets Manager** for API keys
- **Application Load Balancer** for routing

## 📚 Documentation

- [API Documentation](./docs/api.md)
- [Architecture Guide](./docs/architecture.md)
- [Deployment Guide](./docs/deployment.md)
- [Development Guide](./docs/development.md)

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.
