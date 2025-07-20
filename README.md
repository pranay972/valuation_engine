# Financial Valuation Engine

A comprehensive financial valuation platform with advanced DCF modeling, Monte Carlo simulations, sensitivity analysis, and scenario modeling capabilities.

## 🚀 Features

### Core Valuation Methods
- **WACC DCF**: Traditional weighted average cost of capital discounted cash flow
- **APV DCF**: Adjusted present value discounted cash flow
- **Multiples Analysis**: Comparable company and transaction multiples
- **Scenario Analysis**: Multiple scenario modeling with probability weights

### Advanced Analytics
- **Monte Carlo Simulations**: 1,000-10,000 runs with custom variable distributions
- **Sensitivity Analysis**: Multi-dimensional sensitivity tables
- **Risk Assessment**: Statistical analysis with percentiles and confidence intervals
- **Data Visualization**: Interactive charts and tables

### User Experience
- **Modern Web Interface**: React-based frontend with Material-UI
- **Real-time Validation**: Form validation with error handling
- **Data Export**: CSV download for all results
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: Full keyboard navigation and screen reader support

## 📁 Project Structure

```
valuation/
├── backend/               # Python backend package
│   ├── core/             # Core business logic
│   │   ├── valuation/    # Valuation modules
│   │   │   ├── dcf.py    # DCF calculations
│   │   │   ├── monte_carlo.py # Monte Carlo simulations
│   │   │   ├── sensitivity.py # Sensitivity analysis
│   │   │   ├── scenario.py    # Scenario modeling
│   │   │   └── multiples.py   # Multiples analysis
│   │   ├── financial/    # Financial calculations
│   │   │   ├── drivers.py     # Financial drivers
│   │   │   └── wacc.py        # WACC calculations
│   │   └── models/       # Data models
│   │       └── params.py      # Valuation parameters
│   ├── services/         # Service layer
│   │   └── valuation_service.py # Business logic
│   ├── utils/            # Utilities
│   │   ├── exceptions.py # Custom exceptions
│   │   ├── validation.py # Data validation
│   │   └── cache.py      # Caching system
│   ├── config/           # Configuration
│   │   └── logging.py    # Logging setup
│   └── main.py           # FastAPI application
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   └── App.js        # Main application
│   └── package.json      # Frontend dependencies
├── data/                 # Sample data files
│   ├── sample_inputs.txt # Sample valuation inputs
│   └── sample_comps.csv  # Sample comparable companies
├── scripts/              # Build automation
├── test/                 # Test suite
├── docker-compose.yml    # Docker orchestration
├── Makefile              # Build automation
├── pyproject.toml        # Python project config
├── setup.py              # Package setup
├── start_app.py          # Application launcher
└── README.md             # This file
```

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **FastAPI**: Modern, fast web framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **SciPy**: Statistical functions
- **Pydantic**: Data validation

### Frontend
- **React 18**: Modern React with hooks
- **Material-UI**: UI component library
- **React Router**: Client-side routing
- **Custom Hooks**: Reusable logic

### Development Tools
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipeline
- **Pytest**: Testing framework
- **ESLint**: Code linting

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pranayupreti/valuation.git
   cd valuation
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install poetry
   poetry install
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Start the application**
   ```bash
   python start_app.py
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Alternative: Docker Installation

```bash
# Build and start with Docker
docker-compose up -d

# Or use Makefile
make docker-up
```

## 📖 Usage Guide

### 1. Analysis Selection
Choose from available valuation methods:
- **WACC DCF**: Traditional DCF with WACC discount rate
- **APV DCF**: Adjusted present value approach
- **Monte Carlo**: Probabilistic analysis with custom distributions
- **Sensitivity**: Multi-dimensional sensitivity analysis
- **Multiples**: Comparable company analysis
- **Scenarios**: Multiple scenario modeling

### 2. Financial Projections
Input financial data using two modes:
- **Driver-Based**: Input key drivers (revenue growth, margins, etc.)
- **Direct Input**: Input cash flows directly

### 3. Valuation Assumptions
Configure key parameters:
- **WACC**: Weighted average cost of capital
- **Terminal Growth**: Long-term growth rate
- **Tax Rate**: Corporate tax rate
- **Mid-Year Convention**: DCF timing convention

### 4. Advanced Analysis
Configure advanced features:
- **Monte Carlo**: Variable distributions and simulation runs
- **Sensitivity**: Parameter ranges and step sizes
- **Scenarios**: Multiple scenarios with probabilities
- **Multiples**: Comparable company data upload

### 5. Results Analysis
Review comprehensive results:
- **Valuation Summary**: Key metrics and ranges
- **Detailed Tables**: Year-by-year projections
- **Statistical Analysis**: Percentiles and confidence intervals
- **Export Options**: CSV download functionality

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
API_WORKERS=4

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8001
REACT_APP_ENVIRONMENT=development

# Database Configuration (if using)
DATABASE_URL=sqlite:///./valuation.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=valuation.log
```

### Sample Data
The application includes sample data files:
- `sample_inputs.txt`: Example valuation inputs
- `sample_comps.csv`: Sample comparable companies

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest test/test_valuation.py

# Run with coverage
pytest --cov=valuation
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Test API endpoints
pytest test/test_api.py

# Test frontend integration
pytest test/test_frontend_integration.py
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
```bash
# Backend
cd api
uvicorn main:app --host 0.0.0.0 --port 8001

# Frontend
cd frontend
npm run build
npm start
```

## 📊 API Documentation

### Core Endpoints
- `POST /api/valuation`: Run valuation analysis
- `GET /health`: Health check
- `GET /docs`: Interactive API documentation

### Request Format
```json
{
  "analyses": ["WACC DCF", "Monte Carlo"],
  "financial_projections": {
    "input_mode": "driver",
    "revenue": [1000000, 1100000, 1210000],
    "ebit_margin": 0.20,
    "capex": [50000, 55000, 60500],
    "depreciation": [40000, 44000, 48400],
    "nwc_changes": [10000, 11000, 12100],
    "share_count": 100000000,
    "cost_of_debt": 0.05,
    "current_debt": 0,
    "debt_schedule": {}
  },
  "valuation_assumptions": {
    "wacc": 0.12,
    "terminal_growth": 0.025,
    "tax_rate": 0.25,
    "mid_year_convention": true
  },
  "advanced_analysis": {
    "mc_runs": 2000,
    "variable_specs": {
      "wacc": {
        "dist": "normal",
        "params": {"loc": 0.12, "scale": 0.01}
      }
    }
  }
}
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest`
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to the branch: `git push origin feature/new-feature`
8. Submit a pull request

### Code Style
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ESLint configuration
- **Documentation**: Add JSDoc comments for functions
- **Tests**: Maintain >90% code coverage

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Financial Modeling**: Based on industry-standard DCF methodologies
- **Statistical Analysis**: Leverages SciPy and NumPy for robust calculations
- **UI/UX**: Built with Material-UI for consistent, accessible design
- **Testing**: Comprehensive test suite with pytest

## 📞 Support

For questions, issues, or contributions:
- **Issues**: [GitHub Issues](https://github.com/pranayupreti/valuation/issues)
- **Email**: pranay@example.com
- **Documentation**: [Technical Documentation](TECHNICAL_DOCUMENTATION.md)

---

**Built with ❤️ by Pranay Upreti**
