# Financial Valuation Backend

Flask backend for the Financial Valuation Application with comprehensive API endpoints and financial calculation engine.

## 🎯 Features

- RESTful API endpoints for financial analysis
- Integration with finance_core calculation engine
- Background task processing with Celery
- PostgreSQL database with SQLAlchemy ORM
- Comprehensive input validation and error handling

## 📊 Analysis Types

- **DCF (WACC)** - Standard discounted cash flow valuation
- **APV** - Adjusted Present Value method
- **Comparable Multiples** - Relative valuation using peer ratios
- **Scenario Analysis** - Multiple parameter combinations
- **Sensitivity Analysis** - Parameter impact analysis
- **Monte Carlo** - Risk analysis with probability distributions

## 🔗 API Endpoints

### Analysis Management
- `GET /api/analysis/types` - Get available analysis types
- `POST /api/analysis` - Create new analysis
- `GET /api/analysis/{id}` - Get specific analysis

### Valuation Processing
- `POST /api/valuation/{id}/inputs` - Submit input data
- `GET /api/valuation/{id}/inputs` - Get input data

### Results
- `GET /api/results/{id}/results` - Get analysis results
- `GET /api/results/{id}/status` - Get processing status

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── services/         # Business logic services
│   └── models.py         # Data models
├── finance_core/         # Financial calculation engine
├── app.py               # Main Flask application
└── pyproject.toml       # Dependencies
``` 