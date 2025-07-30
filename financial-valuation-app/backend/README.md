# Financial Valuation Backend

Flask backend for the Financial Valuation Application.

## Features

- RESTful API endpoints for financial analysis
- Integration with finance_core calculation engine
- Background task processing with Celery
- PostgreSQL database with SQLAlchemy ORM
- Comprehensive input validation and error handling

## Analysis Types

- DCF Valuation (WACC)
- APV Valuation
- Comparable Multiples
- Scenario Analysis
- Sensitivity Analysis
- Monte Carlo Simulation

## API Endpoints

- `GET /api/analysis/types` - Get available analysis types
- `POST /api/analysis` - Create new analysis
- `GET /api/analysis/{id}` - Get specific analysis
- `POST /api/valuation/{id}/inputs` - Submit input data
- `GET /api/valuation/{id}/inputs` - Get input data
- `GET /api/results/{id}/results` - Get analysis results
- `GET /api/results/{id}/status` - Get processing status 