# Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Core Algorithms](#core-algorithms)
5. [API Reference](#api-reference)
6. [Data Models](#data-models)
7. [Configuration](#configuration)
8. [Testing Strategy](#testing-strategy)
9. [Performance Optimization](#performance-optimization)
10. [Security Considerations](#security-considerations)
11. [Deployment Guide](#deployment-guide)
12. [Troubleshooting](#troubleshooting)

## Architecture Overview

### System Architecture
```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   React Frontend│ ◄──────────────► │  FastAPI Backend│
│   (Port 3000)   │                 │   (Port 8001)   │
└─────────────────┘                 └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │  Core Valuation │
                                    │     Engine      │
                                    └─────────────────┘
```

### Technology Stack
- **Backend**: Python 3.8+, FastAPI, Pandas, NumPy, SciPy
- **Frontend**: React 18, Material-UI, React Router
- **Data Processing**: Pandas for financial calculations
- **Statistical Analysis**: SciPy for Monte Carlo and sensitivity
- **API**: FastAPI with automatic OpenAPI documentation
- **Testing**: Pytest for backend, Jest for frontend

## Backend Architecture

### Core Modules

#### 1. Valuation Engine (`valuation.py`)
```python
class ValuationEngine:
    """Main valuation calculation engine"""
    
    def calculate_dcf(self, projections, assumptions):
        """Calculate DCF valuation using WACC or APV method"""
        
    def calculate_terminal_value(self, final_fcf, growth, wacc):
        """Calculate terminal value using Gordon Growth Model"""
        
    def calculate_enterprise_value(self, fcf_series, terminal_value, wacc):
        """Calculate enterprise value from FCF and terminal value"""
```

#### 2. Monte Carlo Engine (`montecarlo.py`)
```python
class MonteCarloEngine:
    """Monte Carlo simulation engine"""
    
    def run_simulation(self, base_data, variable_specs, runs):
        """Run Monte Carlo simulation with specified variables"""
        
    def generate_distributions(self, specs):
        """Generate probability distributions for variables"""
        
    def calculate_statistics(self, results):
        """Calculate statistical measures from simulation results"""
```

#### 3. Sensitivity Analysis (`sensitivity.py`)
```python
class SensitivityEngine:
    """Sensitivity analysis engine"""
    
    def create_sensitivity_table(self, base_data, ranges, steps):
        """Create multi-dimensional sensitivity table"""
        
    def calculate_impact(self, base_value, variations):
        """Calculate impact of parameter variations"""
```

#### 4. Multiples Analysis (`multiples.py`)
```python
class MultiplesEngine:
    """Comparable multiples analysis engine"""
    
    def calculate_multiples(self, comps_data, target_metrics):
        """Calculate valuation multiples from comparable companies"""
        
    def filter_outliers(self, multiples, method='iqr'):
        """Remove statistical outliers from multiples data"""
```

### Data Flow
1. **Request Reception**: FastAPI receives JSON request
2. **Validation**: Pydantic models validate input data
3. **Processing**: Core engines perform calculations
4. **Caching**: Results cached for performance
5. **Response**: JSON response with results and metadata

## Frontend Architecture

### Component Hierarchy
```
App
├── Header
├── ValuationForm
│   ├── AnalysisSelection
│   ├── FinancialProjections
│   ├── ValuationAssumptions
│   └── AdvancedAnalysis
├── Results
└── Footer
```

### State Management
- **Local State**: React hooks for component-level state
- **Form State**: Controlled components with validation
- **API State**: Custom hooks for API calls and loading states

### Custom Hooks

#### useApi Hook
```javascript
const { loading, error, runValuation, clearError } = useApi();

// Features:
// - Loading state management
// - Error handling with specific messages
// - Request timeout (30 seconds)
// - Request cancellation
```

#### useFormValidation Hook
```javascript
const { errors, validateNumber, validatePercentage, hasErrors } = useFormValidation();

// Features:
// - Field-level error management
// - Validation functions for different data types
// - Error clearing and setting
```

## Core Algorithms

### 1. DCF Valuation Algorithm

#### WACC DCF Method
```python
def calculate_wacc_dcf(revenue, ebit_margin, capex, depreciation, nwc_changes, 
                      wacc, terminal_growth, tax_rate, share_count):
    """
    Calculate DCF valuation using WACC method
    
    Steps:
    1. Calculate EBIT = Revenue × EBIT Margin
    2. Calculate NOPAT = EBIT × (1 - Tax Rate)
    3. Calculate FCF = NOPAT + Depreciation - CapEx - NWC Changes
    4. Calculate Terminal Value = Final FCF × (1 + g) / (WACC - g)
    5. Discount FCF and Terminal Value to present
    6. Calculate Enterprise Value = Sum of discounted values
    7. Calculate Equity Value = Enterprise Value - Net Debt
    8. Calculate Price per Share = Equity Value / Share Count
    """
```

#### APV DCF Method
```python
def calculate_apv_dcf(revenue, ebit_margin, capex, depreciation, nwc_changes,
                     unlevered_cost, cost_of_debt, tax_rate, debt_schedule):
    """
    Calculate DCF valuation using APV method
    
    Steps:
    1. Calculate unlevered FCF (same as WACC method)
    2. Calculate unlevered value by discounting at unlevered cost of capital
    3. Calculate tax shield value from debt schedule
    4. Enterprise Value = Unlevered Value + Tax Shield Value
    5. Equity Value = Enterprise Value - Net Debt
    """
```

### 2. Monte Carlo Simulation Algorithm

```python
def monte_carlo_simulation(base_data, variable_specs, runs):
    """
    Monte Carlo simulation algorithm
    
    Steps:
    1. Define probability distributions for key variables
    2. Generate random samples for each variable
    3. Run DCF calculation with each sample set
    4. Collect all valuation results
    5. Calculate statistical measures (mean, median, percentiles)
    6. Generate confidence intervals
    """
    
    # Distribution types supported:
    # - Normal: loc (mean), scale (standard deviation)
    # - Uniform: low, high
    # - Triangular: low, mode, high
    # - Lognormal: loc, scale
```

### 3. Sensitivity Analysis Algorithm

```python
def sensitivity_analysis(base_data, parameter_ranges, steps):
    """
    Sensitivity analysis algorithm
    
    Steps:
    1. Define parameter ranges and step sizes
    2. Create grid of parameter combinations
    3. Run valuation for each combination
    4. Calculate impact metrics
    5. Generate sensitivity tables
    6. Identify key value drivers
    """
```

### 4. Multiples Analysis Algorithm

```python
def multiples_analysis(comps_data, target_metrics):
    """
    Comparable multiples analysis
    
    Steps:
    1. Calculate valuation multiples for comparable companies
    2. Remove statistical outliers
    3. Calculate mean, median, and range
    4. Apply multiples to target company metrics
    5. Calculate implied enterprise values
    6. Generate valuation ranges
    """
```

## API Reference

### Core Endpoints

#### POST /api/valuation
Run comprehensive valuation analysis.

**Request Body:**
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

**Response:**
```json
{
  "status": "success",
  "results": {
    "wacc_dcf": {
      "enterprise_value": 15000000,
      "equity_value": 15000000,
      "price_per_share": 0.15,
      "fcf_series": [...],
      "terminal_value": 12000000
    },
    "monte_carlo": {
      "statistics": {
        "mean": 0.15,
        "median": 0.14,
        "std": 0.02,
        "percentiles": {
          "5": 0.12,
          "25": 0.13,
          "50": 0.14,
          "75": 0.16,
          "95": 0.18
        }
      },
      "distribution": [...]
    }
  },
  "metadata": {
    "execution_time": 2.5,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "2.0.0"
}
```

### Error Responses
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid WACC value. Must be between 0 and 1.",
    "details": {
      "field": "wacc",
      "value": 1.5
    }
  }
}
```

## Data Models

### Pydantic Models

#### FinancialProjections
```python
class FinancialProjections(BaseModel):
    input_mode: Literal["driver", "direct"]
    revenue: List[float]
    ebit_margin: float = Field(ge=0, le=1)
    capex: List[float]
    depreciation: List[float]
    nwc_changes: List[float]
    fcf_series: Optional[List[float]] = None
    share_count: int = Field(gt=0)
    cost_of_debt: float = Field(ge=0, le=1)
    current_debt: float = Field(ge=0)
    debt_schedule: Dict[str, float] = {}
```

#### ValuationAssumptions
```python
class ValuationAssumptions(BaseModel):
    wacc: float = Field(ge=0, le=1)
    terminal_growth: float = Field(ge=-0.1, le=0.1)
    tax_rate: float = Field(ge=0, le=1)
    mid_year_convention: bool = True
```

#### MonteCarloSpec
```python
class MonteCarloSpec(BaseModel):
    mc_runs: int = Field(ge=100, le=10000)
    variable_specs: Dict[str, VariableSpec]
    
class VariableSpec(BaseModel):
    dist: Literal["normal", "uniform", "triangular", "lognormal"]
    params: Dict[str, float]
```

### Validation Rules
- **Revenue**: Must be positive and same length as other series
- **EBIT Margin**: Between 0% and 100%
- **WACC**: Between 0% and 100%
- **Terminal Growth**: Between -10% and +10%
- **Terminal Growth < WACC**: Prevents infinite terminal value
- **Monte Carlo Runs**: Between 100 and 10,000

## Configuration

### Environment Variables
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
API_WORKERS=4
API_TIMEOUT=30

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=valuation.log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Cache Configuration
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Security Configuration
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=["localhost", "127.0.0.1"]
```

### Configuration Files

#### config.py
```python
class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_workers: int = 4
    api_timeout: int = 30
    
    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: str = "valuation.log"
    
    # Cache Settings
    cache_ttl: int = 3600
    cache_max_size: int = 1000
    
    class Config:
        env_file = ".env"
```

## Testing Strategy

### Backend Testing

#### Unit Tests
```python
# Test valuation calculations
def test_wacc_dcf_calculation():
    """Test WACC DCF calculation with known inputs"""
    result = calculate_wacc_dcf(
        revenue=[1000000, 1100000],
        ebit_margin=0.20,
        wacc=0.12,
        terminal_growth=0.025
    )
    assert result['enterprise_value'] > 0
    assert result['equity_value'] > 0
```

#### Integration Tests
```python
# Test API endpoints
def test_valuation_endpoint():
    """Test complete valuation API endpoint"""
    response = client.post("/api/valuation", json=test_data)
    assert response.status_code == 200
    assert "results" in response.json()
```

#### Performance Tests
```python
# Test Monte Carlo performance
def test_monte_carlo_performance():
    """Test Monte Carlo simulation performance"""
    start_time = time.time()
    result = run_monte_carlo(base_data, specs, 1000)
    execution_time = time.time() - start_time
    assert execution_time < 5.0  # Should complete within 5 seconds
```

### Frontend Testing

#### Component Tests
```javascript
// Test form validation
test('validates required fields', () => {
  render(<ValuationForm />);
  const submitButton = screen.getByText('Run Valuation');
  fireEvent.click(submitButton);
  expect(screen.getByText('Revenue is required')).toBeInTheDocument();
});
```

#### Integration Tests
```javascript
// Test API integration
test('submits form data to API', async () => {
  const mockApi = jest.fn();
  render(<ValuationForm onSubmit={mockApi} />);
  
  // Fill form and submit
  fireEvent.click(screen.getByText('Run Valuation'));
  
  await waitFor(() => {
    expect(mockApi).toHaveBeenCalledWith(expect.objectContaining({
      analyses: ['WACC DCF']
    }));
  });
});
```

### Test Coverage Targets
- **Backend**: >90% code coverage
- **Frontend**: >80% code coverage
- **Critical Paths**: 100% coverage
- **API Endpoints**: 100% coverage

## Performance Optimization

### Backend Optimizations

#### Caching Strategy
```python
# Redis caching for expensive calculations
@cache(ttl=3600)
def calculate_dcf(projections, assumptions):
    """Cache DCF calculations for 1 hour"""
    return perform_dcf_calculation(projections, assumptions)
```

#### Database Optimization
- **Connection Pooling**: Reuse database connections
- **Query Optimization**: Use indexes for frequently accessed data
- **Caching**: Cache frequently accessed data

#### Algorithm Optimization
```python
# Vectorized calculations using NumPy
def calculate_fcf_vectorized(revenue, ebit_margin, capex, depreciation, nwc_changes):
    """Vectorized FCF calculation for better performance"""
    revenue_array = np.array(revenue)
    ebit = revenue_array * ebit_margin
    fcf = ebit * (1 - tax_rate) + np.array(depreciation) - np.array(capex) - np.array(nwc_changes)
    return fcf.tolist()
```

### Frontend Optimizations

#### React Optimizations
```javascript
// Memoize expensive calculations
const memoizedResults = useMemo(() => {
  return calculateValuationMetrics(data);
}, [data]);

// Lazy load components
const AdvancedAnalysis = lazy(() => import('./AdvancedAnalysis'));
```

#### Bundle Optimization
- **Code Splitting**: Split code into smaller chunks
- **Tree Shaking**: Remove unused code
- **Minification**: Compress JavaScript and CSS

### Performance Monitoring
```python
# Performance metrics
class PerformanceMetrics:
    def __init__(self):
        self.execution_times = []
        self.memory_usage = []
    
    def record_execution_time(self, operation, duration):
        """Record execution time for performance monitoring"""
        self.execution_times.append({
            'operation': operation,
            'duration': duration,
            'timestamp': datetime.now()
        })
```

## Security Considerations

### Input Validation
```python
# Comprehensive input validation
def validate_financial_data(data: FinancialProjections) -> ValidationResult:
    """Validate all financial data inputs"""
    
    # Check for negative values
    if any(r < 0 for r in data.revenue):
        return ValidationResult(valid=False, error="Revenue cannot be negative")
    
    # Check series lengths
    if len(set([len(data.revenue), len(data.capex), len(data.depreciation)])) > 1:
        return ValidationResult(valid=False, error="All series must have same length")
    
    return ValidationResult(valid=True)
```

### API Security
- **Rate Limiting**: Prevent abuse with rate limiting
- **CORS Configuration**: Restrict cross-origin requests
- **Input Sanitization**: Sanitize all user inputs
- **Error Handling**: Don't expose sensitive information in errors

### Data Security
- **Encryption**: Encrypt sensitive data at rest
- **Access Control**: Implement proper access controls
- **Audit Logging**: Log all data access and modifications

## Deployment Guide

### Docker Deployment
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

```dockerfile
# Frontend Dockerfile
FROM node:16-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8001:8001"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8001
    volumes:
      - ./logs:/app/logs
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8001
    depends_on:
      - backend
```

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Troubleshooting

### Common Issues

#### 1. Memory Issues
**Problem**: Large Monte Carlo simulations causing memory errors
**Solution**: 
- Reduce Monte Carlo runs (use 1,000-2,000 for testing)
- Implement streaming for large datasets
- Add memory monitoring

#### 2. Performance Issues
**Problem**: Slow calculation times
**Solution**:
- Enable caching for repeated calculations
- Use vectorized operations with NumPy
- Implement parallel processing for Monte Carlo

#### 3. Validation Errors
**Problem**: Input validation failures
**Solution**:
- Check data types and ranges
- Ensure all series have same length
- Verify terminal growth < WACC

#### 4. API Connection Issues
**Problem**: Frontend can't connect to backend
**Solution**:
- Check CORS configuration
- Verify API URL in frontend
- Check firewall settings

### Debug Tools
```python
# Debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Performance profiling
import cProfile
import pstats

def profile_function(func, *args):
    """Profile function performance"""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args)
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    return result
```

### Monitoring
```python
# Health check monitoring
@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent()
    }
```

---

This technical documentation provides comprehensive information about the Financial Valuation Engine's architecture, algorithms, and implementation details. For additional support, refer to the main README or contact the development team. 