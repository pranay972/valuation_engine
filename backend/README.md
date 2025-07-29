# Valuation Backend

Flask-based REST API backend for the financial valuation web application.

## Features

- **RESTful API**: Clean API endpoints for valuation calculations
- **Finance Core Integration**: Uses the existing `finance_core` calculator
- **Docker Support**: Containerized deployment
- **Poetry Management**: Modern Python dependency management
- **CORS Support**: Cross-origin resource sharing enabled
- **Error Handling**: Comprehensive error handling and validation
- **Swagger UI**: Interactive API documentation

## API Endpoints

### POST `/api/valuation/calculate`
Calculate comprehensive valuation using DCF, APV, and other methods.

**Request Body:**
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

**Response:**
```json
{
  "company_name": "TechCorp Inc.",
  "valuation_date": "2024-01-01",
  "dcf_wacc": {
    "enterprise_value": 2500.0,
    "equity_value": 2350.0,
    "price_per_share": 52.0,
    "free_cash_flows_after_tax_fcff": [...],
    "terminal_value": 1500.0,
    "present_value_of_terminal": 1200.0
  },
  "apv": {...},
  "comparable_multiples": {...},
  "scenarios": {...},
  "sensitivity": {...},
  "monte_carlo": {...}
}
```

### GET `/api/valuation/sample`
Get sample valuation data for testing.

### GET `/api/valuation/health`
Health check endpoint.

### GET `/health`
Main application health check.

### GET `/api/docs`
Interactive API documentation (Swagger UI).

### GET `/static/swagger.json`
OpenAPI specification in JSON format.

## Setup

### Prerequisites
- Python 3.9+
- Poetry
- Docker (optional)

### Local Development

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Run the application:**
   ```bash
   poetry run python run.py
   ```

3. **Run tests:**
   ```bash
   poetry run pytest
   ```

### Docker Development

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Or build and run manually:**
   ```bash
   docker build -t valuation-backend .
   docker run -p 5000:5000 valuation-backend
   ```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── api/
│   │   ├── __init__.py
│   │   └── valuation.py     # Valuation API endpoints
│   └── services/
│       ├── __init__.py
│       └── valuation_service.py  # Business logic
├── tests/
│   ├── __init__.py
│   └── test_valuation_service.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
├── run.py                   # Application entry point
└── README.md
```

## Environment Variables

- `FLASK_DEBUG`: Enable debug mode (default: True)
- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Flask secret key

## Development

### Code Formatting
```bash
poetry run black .
poetry run flake8 .
```

### Running Tests
```bash
poetry run pytest
poetry run pytest -v  # Verbose output
poetry run pytest -k "test_name"  # Run specific test
```

## API Documentation

The API follows RESTful principles and returns JSON responses. All endpoints support CORS for frontend integration.

### Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "details": "Additional error details (in debug mode)"
}
```

### Status Codes

- `200`: Success
- `400`: Bad Request (validation errors)
- `500`: Internal Server Error

## API Documentation

The API includes comprehensive Swagger UI documentation available at `/api/docs` when the server is running. This provides:

- **Interactive Testing**: Test API endpoints directly from the browser
- **Request/Response Examples**: See example data structures
- **Parameter Validation**: Understand required and optional fields
- **Response Schemas**: View detailed response structures

## Integration with Frontend

The backend is designed to work seamlessly with a React frontend. CORS is configured to allow cross-origin requests from the frontend application. 