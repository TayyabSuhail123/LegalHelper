# ContractCopilot - AI-Powered Legal Document Analysis System

> A production-grade multi-agent AI system that provides comprehensive legal document analysis using specialized agents for risk assessment, fraud detection, and legal guidance.

## 🎯 Project Overview

ContractCopilot is an enterprise-ready legal document analysis platform powered by a sophisticated multi-agent AI architecture. The system deploys specialized AI agents to analyze uploaded legal documents (PDF, DOCX, or text) and provides comprehensive reports covering document summaries, risk assessments, fraud detection, legal implications, and actionable recommendations.

## 🤖 Multi-Agent Architecture

Our system employs **5 specialized AI agents**, each with dedicated expertise:

### 📄 **Document Summarizer Agent**
- Provides clear, plain-English document summaries
- Identifies document type, purpose, and key parties
- Extracts important dates and deadlines
- Makes legal documents accessible to non-lawyers

### ⚠️ **Risk Assessment Agent**
- Analyzes potential legal risks and liabilities
- Categorizes risks by severity (LOW/MEDIUM/HIGH/CRITICAL)
- Identifies problematic clauses and unfavorable terms
- Provides specific recommendations for each risk

### 🛡️ **Fraud Detection Agent**
- Scans for suspicious clauses and hidden fees
- Detects deceptive language and pressure tactics
- Identifies terms that heavily favor one party
- Calculates fraud risk scores (0-10 scale)

### ⚖️ **Legal Advisor Agent**
- Explains legal implications and consequences
- Clarifies rights and obligations for all parties
- Identifies enforceability issues
- Provides compliance guidance

### 📋 **Action Planner Agent**
- Creates specific action plans and next steps
- Prioritizes immediate vs. long-term actions
- Identifies deadlines and critical timeframes
- Provides structured recommendations timeline

## 🏗️ Architecture

This is a modern full-stack application with organized multi-agent backend:

- **`frontend/`** - Next.js 15.5.5 with React 19 and TypeScript
- **`backend/`** - Python FastAPI with organized multi-agent system
- **`infra/`** - Terraform infrastructure as code for AWS deployment

### Backend Agent Organization
```
backend/app/agents/
├── base_agent.py              # Base class for all agents
├── document_summarizer.py     # Document analysis and summarization
├── risk_assessor.py          # Risk identification and assessment
├── fraud_detector.py         # Fraud and suspicious clause detection
├── legal_advisor.py          # Legal implications and guidance
├── action_planner.py         # Action planning and recommendations
└── prompts/                  # Dedicated prompt files for each agent
    ├── document_summarizer.prompt
    ├── risk_assessor.prompt
    ├── fraud_detector.prompt
    ├── legal_advisor.prompt
    └── action_planner.prompt
```

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

- **Backend API**: http://localhost:8000 (Docker containerized with multi-agent system)
- **Frontend App**: http://localhost:3000 (Next.js with live reloading)
- **API Docs**: http://localhost:8000/docs (Interactive Swagger documentation)
- **Redis**: http://localhost:6379 (Docker containerized for session management)

### Note on Docker Setup

- The backend and Redis run in Docker containers for consistency
- The frontend runs locally for faster development iteration  
- Use `docker-compose up -d` to start only the backend services
- Use `npm start` in the frontend directory for live reloading
- The multi-agent system is organized with individual agent files and dedicated prompts

### Current Tech Stack

**Backend:**
- FastAPI with Python 3.11+
- OpenAI GPT-4 Turbo for AI processing
- Multi-agent architecture with specialized agents
- Docker containerization
- Redis for session management

**Frontend:**
- Next.js 15.5.5 with App Router
- React 19 with TypeScript
- Tailwind CSS for styling
- Real-time status updates
- Responsive design

## 🚀 Current Features (✅ Built)

### **Core Multi-Agent Analysis System**
- ✅ **5 Specialized AI Agents** with dedicated expertise areas
- ✅ **Organized Agent Architecture** with individual prompt files
- ✅ **GPT-4 Turbo Integration** for handling large documents
- ✅ **Multi-format Support**: PDF, DOCX, and plain text contracts
- ✅ **Comprehensive Analysis Pipeline** covering all aspects of legal documents

### **Document Processing & Analysis**
- ✅ **Document Summarization** in plain English
- ✅ **Risk Assessment** with severity classification (LOW/MEDIUM/HIGH/CRITICAL)
- ✅ **Fraud Detection** with suspicious clause identification
- ✅ **Legal Implications Analysis** with rights and obligations breakdown
- ✅ **Action Planning** with prioritized recommendations and timelines

### **Technical Infrastructure**
- ✅ **FastAPI Backend** with async processing
- ✅ **Next.js 15.5.5 Frontend** with React 19 and TypeScript
- ✅ **Docker Containerization** for backend services
- ✅ **Redis Integration** for session management
- ✅ **File Upload & Processing** with validation
- ✅ **Error Handling & Logging** throughout the system

### **User Experience**
- ✅ **Intuitive Upload Interface** with drag-and-drop support
- ✅ **Real-time Processing Status** with progress indicators
- ✅ **Comprehensive Results Display** with organized sections
- ✅ **Mobile-Responsive Design** for all devices
- ✅ **Clean, Professional UI** with modern styling

## 🔮 Planned Features (🚧 Coming Soon)

### **Enhanced AI Capabilities**
- 🚧 **Document Comparison Agent** - Compare multiple contracts side-by-side
- 🚧 **Contract Templates Generator** - Create contract templates based on analysis
- 🚧 **Clause Library Integration** - Build searchable database of analyzed clauses
- 🚧 **Language Translation Agent** - Multi-language document support

### **Advanced Analysis Features**
- 🚧 **Document Chunking for Large Files** - Handle extremely large documents (100+ pages)
- 🚧 **Rate Limiting & Queue Management** - Handle high-volume processing
- 🚧 **Batch Document Processing** - Analyze multiple documents simultaneously
- 🚧 **Historical Analysis Tracking** - Track changes in contract terms over time


### **Integration & Export**
- 🚧 **PDF Report Generation** - Professional formatted reports
- 🚧 **API for Third-party Integration** - Connect with legal software
- 🚧 **Webhook Notifications** - Real-time analysis completion alerts
- 🚧 **Export to Legal Databases** - Integration with case management systems

### **Performance & Monitoring**
- 🚧 **Langfuse LLM Tracing** - Detailed AI performance monitoring
- 🚧 **Advanced Caching** - Reduce processing time for similar documents
- 🚧 **Performance Analytics Dashboard** - System usage and performance metrics
- 🚧 **Cost Optimization** - Smart model selection based on document complexity

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
