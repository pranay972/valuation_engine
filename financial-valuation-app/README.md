# Financial Valuation Application

A professional financial valuation system with React frontend and Flask backend supporting 6 analysis methods.

## 🎯 Analysis Methods

- **DCF (WACC)** - Standard discounted cash flow valuation
- **APV** - Adjusted Present Value method
- **Comparable Multiples** - Relative valuation using peer ratios
- **Scenario Analysis** - Multiple parameter combinations
- **Sensitivity Analysis** - Parameter impact analysis
- **Monte Carlo** - Risk analysis with probability distributions

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose

### Start Application
```bash
# Quick start (recommended)
./quick-start.sh

# Or manual start
docker-compose up --build -d
```

### Access URLs
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **Swagger UI**: http://localhost:8001/api/docs
- **Celery Flower (Monitoring)**: http://localhost:5555

## 📁 Project Structure

```
financial-valuation-app/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   └── package.json
├── backend/                 # Flask backend
│   ├── app/                # Flask application
│   │   ├── api/           # API endpoints
│   │   ├── services/      # Business logic services
│   │   └── models.py      # Database models
│   ├── finance_core/       # Financial calculation engine
│   └── pyproject.toml
├── docker-compose.yml      # Docker orchestration with Celery
└── quick-start.sh          # Quick start script
```

## 🐛 Celery Background Processing

The application uses Celery for background task processing:

- **Celery Worker**: Processes financial analysis tasks
- **Celery Beat**: Handles scheduled tasks (future feature)
- **Celery Flower**: Web-based monitoring and debugging interface
- **Redis**: Message broker and result backend

### Celery Configuration
- **Worker Isolation**: `worker_max_tasks_per_child=1` ensures fresh environment per task
- **Memory Limits**: `worker_max_memory_per_child=100000` (100MB) prevents memory leaks
- **Health Checks**: Automatic worker health monitoring and restart

## 📱 Application Flow

1. **Analysis Selection** - Choose one or more analysis types
2. **Input Form** - Enter financial data (revenue, margins, WACC, etc.)
3. **Results** - View detailed results and comparison charts

## 🔧 Management Commands

```bash
# View logs
docker-compose logs -f                    # All services
docker-compose logs -f backend           # Backend only
docker-compose logs -f celery            # Celery worker only
docker-compose logs -f celery-flower     # Monitoring interface

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up --build -d

# Start specific service
docker-compose up -d redis               # Start Redis only
docker-compose up -d celery             # Start Celery worker only
docker-compose up -d backend            # Start Backend only

# Monitor Celery
docker-compose exec celery celery -A app.services.celery_service.celery inspect active
docker-compose exec celery celery -A app.services.celery_service.celery inspect stats

# Run tests
./run_tests.sh
```

## 📊 API Endpoints

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs

### Core Endpoints
- `GET /api/analysis/types` - Get available analysis types
- `POST /api/analysis` - Create new analysis
- `POST /api/valuation/{id}/inputs` - Submit input data
- `GET /api/results/{id}/results` - Get analysis results
- `GET /api/results/{id}/status` - Get processing status

### Data Management
- `GET /api/csv/sample` - Download sample CSV template
- `POST /api/csv/upload` - Upload CSV data file

## 🧪 Testing

```bash
# Run all tests
./run_tests.sh

# Backend tests only
cd backend && python -m pytest tests/ -v

# Frontend tests only
cd frontend && npm test
```

## 🚀 Next Steps

1. Start the application using `./quick-start.sh`
2. Access the frontend at http://localhost:3000
3. Select analysis types and enter financial data
4. View comprehensive results and charts

## 🔮 Future Enhancements

- [ ] Real-time charts with Recharts
- [ ] PDF report generation
- [ ] Excel export functionality
- [ ] User authentication
- [ ] Advanced charting options
- [ ] Mobile responsive design

## 🆘 Troubleshooting

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Restart services: `docker-compose restart`
3. Rebuild containers: `docker-compose up --build -d`
4. Check Docker status: `docker ps` 