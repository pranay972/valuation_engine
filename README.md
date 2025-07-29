# Financial Valuation Engine

A comprehensive financial valuation system with a modern web API, supporting DCF, APV, Comparable Multiples, Scenario Analysis, Sensitivity Analysis, and Monte Carlo Simulation.

## 🚀 Features

### Core Valuation Methods
- **DCF (Discounted Cash Flow)**: WACC-based valuation with circular dependency handling
- **APV (Adjusted Present Value)**: Separate unlevered value and tax shield calculations
- **Comparable Multiples**: EV/EBITDA, P/E, and other industry multiples
- **Scenario Analysis**: Optimistic, base case, and pessimistic scenarios
- **Sensitivity Analysis**: Parameter sensitivity testing
- **Monte Carlo Simulation**: Risk analysis with probability distributions

### Web API
- **RESTful API**: Clean, documented endpoints
- **Swagger UI**: Interactive API documentation
- **Flask Backend**: Modern Python web framework
- **Docker Support**: Containerized deployment
- **CORS Enabled**: Frontend integration ready

### Development Features
- **CI/CD Pipeline**: Automated testing on commits and PRs
- **Code Quality**: Linting, formatting, and type checking
- **Security Scanning**: Automated security checks
- **Test Coverage**: Comprehensive test suite
- **Documentation**: Detailed API and code documentation

## 📁 Project Structure

```
valuation/
├── .github/workflows/          # GitHub Actions CI/CD
│   ├── ci.yml                 # Full CI/CD pipeline
│   └── test.yml               # Test-only workflow
├── finance_core/              # Core valuation engine
│   ├── finance_calculator.py  # Main calculator class
│   ├── dcf.py                 # DCF calculations
│   ├── wacc.py                # WACC calculations
│   ├── multiples.py           # Comparable multiples
│   ├── scenario.py            # Scenario analysis
│   ├── sensitivity.py         # Sensitivity analysis
│   ├── monte_carlo.py         # Monte Carlo simulation
│   └── test_finance_calculator.py
├── backend/                   # Flask API
│   ├── app/                   # Flask application
│   │   ├── api/              # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── static/           # Static files (Swagger)
│   │   └── swagger.py        # Swagger configuration
│   ├── tests/                # Backend tests
│   ├── Dockerfile            # Docker configuration
│   ├── docker-compose.yml    # Docker Compose
│   └── pyproject.toml        # Poetry configuration
├── pyproject.toml            # Root project configuration
└── README.md                 # This file
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- Poetry (for backend)
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd valuation
   ```

2. **Set up finance_core**
   ```bash
   cd finance_core
   pip install -r requirements.txt
   python -m pytest test_finance_calculator.py -v
   ```

3. **Set up backend**
   ```bash
   cd backend
   poetry install
   poetry run python -m pytest tests/ -v
   poetry run python run.py
   ```

4. **Access the API**
   - API: http://localhost:5001
   - Swagger UI: http://localhost:5001/api/docs
   - Health Check: http://localhost:5001/health

### Docker Deployment

```bash
cd backend
docker-compose up -d
```

## 🧪 Testing

### Run All Tests
```bash
# From project root
pytest finance_core/ backend/tests/ -v
```

### Run Specific Tests
```bash
# Finance core tests
cd finance_core
python -m pytest test_finance_calculator.py -v

# Backend tests
cd backend
poetry run python -m pytest tests/ -v

# API integration tests
cd backend
poetry run python test_swagger.py
```

### Test Coverage
```bash
# Finance core coverage
cd finance_core
python -m pytest --cov=. --cov-report=html

# Backend coverage
cd backend
poetry run python -m pytest --cov=app --cov-report=html
```

## 🔧 CI/CD Pipeline

The project includes comprehensive GitHub Actions workflows:

### Workflows
- **`test.yml`**: Runs tests on commits and PRs
- **`ci.yml`**: Full CI/CD pipeline with security scanning

### Jobs
1. **Test Finance Core**: Unit tests for valuation engine
2. **Test Backend API**: Flask API tests
3. **Test API Integration**: End-to-end API testing
4. **Lint and Format**: Code quality checks
5. **Security Scan**: Security vulnerability scanning
6. **Docker Build**: Container build and test

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

## 📚 API Documentation

### Interactive Documentation
Visit http://localhost:5001/api/docs for interactive Swagger UI documentation.

### Key Endpoints
- `GET /health` - Health check
- `GET /api/valuation/sample` - Get sample data
- `POST /api/valuation/calculate` - Calculate valuation

### Example Request
```json
{
  "company_name": "TechCorp Inc.",
  "valuation_date": "2024-01-01",
  "financial_inputs": {
    "revenue": [1250.0, 1375.0, 1512.5, 1663.8, 1830.1],
    "ebit_margin": 0.18,
    "tax_rate": 0.25,
    "capex": [187.5, 206.3, 226.9, 249.6, 274.5],
    "depreciation": [125.0, 137.5, 151.3, 166.4, 183.0],
    "nwc_changes": [62.5, 68.8, 75.6, 83.2, 91.5],
    "terminal_growth": 0.025,
    "wacc": 0.095,
    "share_count": 45.2,
    "cost_of_debt": 0.065
  }
}
```

## 🔒 Security

The project includes automated security scanning:
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability checker
- **Reports**: Security reports uploaded as artifacts

## 📊 Code Quality

### Tools Used
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing framework

### Configuration
All tools are configured in `pyproject.toml` for consistency across the project.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest finance_core/ backend/tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Ensure all CI/CD checks pass

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: support@valuation.com
- Issues: GitHub Issues
- Documentation: http://localhost:5001/api/docs

## 🚀 Roadmap

- [ ] React frontend
- [ ] Database integration
- [ ] User authentication
- [ ] Advanced analytics dashboard
- [ ] Real-time market data integration
- [ ] Multi-currency support
- [ ] Export functionality (PDF, Excel)
- [ ] API rate limiting
- [ ] Caching layer
- [ ] Performance monitoring 