# CI/CD Setup Guide

This document describes the comprehensive CI/CD pipeline setup for the Financial Valuation Engine project.

## 🚀 Overview

The project includes two GitHub Actions workflows:

1. **`test.yml`** - Simple test workflow for quick feedback
2. **`ci.yml`** - Full CI/CD pipeline with comprehensive checks

## 📋 Workflow Details

### Test Workflow (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- **Test**: Runs all tests in a single job
  - Finance core tests
  - Backend API tests
  - API integration tests
  - Swagger UI accessibility tests

**Duration:** ~3-5 minutes

### Full CI/CD Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**

1. **test-finance-core**
   - Unit tests for valuation engine
   - Coverage reporting
   - Uploads to Codecov

2. **test-backend**
   - Flask API tests
   - Coverage reporting
   - Uploads to Codecov

3. **test-api-integration**
   - End-to-end API testing
   - Swagger UI testing
   - Requires test-backend to pass

4. **lint-and-format**
   - Black code formatting check
   - isort import sorting check
   - flake8 linting
   - mypy type checking

5. **security-scan**
   - Bandit security linter
   - Safety dependency checker
   - Uploads security reports as artifacts

6. **docker-build**
   - Builds Docker image
   - Tests container functionality
   - Requires test-backend and test-finance-core to pass

7. **notify** (on failure)
   - Reports failed jobs
   - Provides debugging information

**Duration:** ~8-12 minutes

## 🛠️ Local Development

### Running Tests Locally

Use the provided test runner script:

```bash
# Run all tests
python run_tests.py

# Run tests with linting
python run_tests.py --lint
```

### Manual Test Commands

```bash
# Finance core tests
cd finance_core
pip install -r requirements.txt
pip install pytest pytest-cov
python -m pytest test_finance_calculator.py -v

# Backend tests
cd backend
poetry install
poetry run python -m pytest tests/ -v

# API integration tests
cd backend
poetry run python run.py &
sleep 10
poetry run python test_swagger.py
```

### Code Quality Checks

```bash
# Install tools
pip install black flake8 isort mypy

# Format code
black finance_core/ backend/

# Sort imports
isort finance_core/ backend/

# Lint code
flake8 finance_core/ backend/ --max-line-length=88

# Type check
mypy finance_core/ backend/ --ignore-missing-imports
```

## 📊 Coverage and Reporting

### Code Coverage
- Finance core coverage uploaded to Codecov
- Backend coverage uploaded to Codecov
- Coverage reports generated in XML and HTML formats

### Security Reports
- Bandit security scan results
- Safety dependency vulnerability reports
- Reports saved as GitHub Actions artifacts

## 🔧 Configuration Files

### Root Configuration (`pyproject.toml`)
- Project metadata
- Tool configurations (Black, isort, flake8, mypy, pytest)
- Coverage settings
- Bandit security settings

### Backend Configuration (`backend/pyproject.toml`)
- Poetry dependencies
- Python version requirements
- Development tools

### Finance Core Configuration (`finance_core/requirements.txt`)
- Core dependencies (numpy, pandas)
- Testing dependencies

## 🚀 Deployment

### Docker Deployment
The CI/CD pipeline includes Docker build and test:

```bash
# Build image
cd backend
docker build -t valuation-backend:latest .

# Test container
docker run -d --name test-backend -p 5001:5001 valuation-backend:latest
curl -f http://localhost:5001/health
docker stop test-backend
docker rm test-backend
```

### Production Deployment
For production deployment, consider:

1. **Environment Variables**
   - Set `FLASK_ENV=production`
   - Configure database connections
   - Set up logging

2. **Security**
   - Enable HTTPS
   - Set up authentication
   - Configure CORS properly

3. **Monitoring**
   - Health checks
   - Performance monitoring
   - Error tracking

## 🔍 Troubleshooting

### Common Issues

1. **Tests Failing Locally but Passing in CI**
   - Check Python version (CI uses 3.11)
   - Ensure all dependencies are installed
   - Clear cache: `poetry cache clear --all pypi`

2. **Docker Build Failures**
   - Check Dockerfile syntax
   - Verify all files are copied correctly
   - Check port conflicts

3. **Security Scan Failures**
   - Review Bandit warnings
   - Update dependencies with vulnerabilities
   - Suppress false positives if needed

### Debugging CI/CD

1. **View Workflow Logs**
   - Go to GitHub Actions tab
   - Click on the workflow run
   - Check individual job logs

2. **Re-run Failed Jobs**
   - Use "Re-run jobs" option in GitHub Actions
   - Re-run specific failed jobs

3. **Local Reproduction**
   - Use the test runner script
   - Check the same Python version
   - Install the same dependencies

## 📈 Best Practices

### Code Quality
- Write tests for new features
- Maintain good test coverage
- Follow PEP 8 style guidelines
- Use type hints where possible

### CI/CD
- Keep workflows fast and focused
- Use caching for dependencies
- Fail fast on critical issues
- Provide clear error messages

### Security
- Regular dependency updates
- Security scanning in CI/CD
- Follow security best practices
- Review security reports

## 🔗 Useful Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Bandit Security Linter](https://bandit.readthedocs.io/)

## 📝 Maintenance

### Regular Tasks
- Update dependencies monthly
- Review and update security tools
- Monitor CI/CD performance
- Update documentation

### Monitoring
- Check workflow success rates
- Monitor test execution times
- Review security scan results
- Track code coverage trends 