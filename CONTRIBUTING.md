# Contributing to ContractCopilot

Thank you for your interest in contributing to ContractCopilot! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- Git

### Setup

1. Fork and clone the repository
2. Run the setup script: `./scripts/setup-dev.sh`
3. Create a new branch: `git checkout -b feature/your-feature-name`

## 📝 Development Guidelines

### Code Style

#### Python (Backend)
- Follow PEP 8 guidelines
- Use Black for code formatting: `python -m black .`
- Use isort for import sorting: `python -m isort .`
- Use type hints for all functions
- Maximum line length: 88 characters

#### TypeScript/React (Frontend)
- Use Prettier for code formatting
- Follow ESLint rules
- Use functional components with hooks
- Use TypeScript strict mode
- Maximum line length: 100 characters

### Commit Messages

Follow the conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Examples:
- `feat(backend): add contract parsing for DOCX files`
- `fix(frontend): resolve file upload validation issue`
- `docs(api): update OpenAPI documentation`

### Testing

#### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
python -m pytest tests/ --cov=app --cov-report=html
```

#### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Code Review Process

1. Create a pull request with a clear description
2. Ensure all tests pass
3. Add tests for new features
4. Update documentation if needed
5. Request review from maintainers

## 🏗️ Project Structure

```
contractcopilot/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Core functionality
│   │   ├── models/    # Pydantic models
│   │   └── services/  # Business logic
│   └── tests/         # Backend tests
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   └── tests/         # Frontend tests
├── infra/             # Terraform infrastructure
└── docs/              # Documentation
```

## 🔧 Development Workflow

### Local Development

1. Start development environment:
   ```bash
   npm run dev
   ```

2. Access applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Docker Development

```bash
docker-compose up -d
```

### Running Tests

```bash
# All tests
npm run test

# Backend only
npm run test:backend

# Frontend only
npm run test:frontend
```

### Linting and Formatting

```bash
# Lint all code
npm run lint

# Format all code
npm run format
```

## 📚 Documentation

- Keep README files up to date
- Document new API endpoints
- Update architecture diagrams when needed
- Add inline code comments for complex logic

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, browser, versions
6. **Screenshots**: If applicable

## 💡 Feature Requests

For new features:

1. Check if the feature already exists or is planned
2. Open an issue with the "feature request" template
3. Describe the use case and benefits
4. Provide implementation ideas if you have them

## 📋 Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated documentation

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
```

## 🏷️ Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create release tag
6. Deploy to staging
7. Deploy to production

## 🤝 Community

- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and best practices
- Follow the code of conduct

## 📞 Getting Help

- GitHub Issues for bugs and features
- GitHub Discussions for questions
- Check documentation first
- Search existing issues before creating new ones

Thank you for contributing to ContractCopilot! 🎉
