# Financial Valuation Application

A simple and fast financial valuation system with React frontend and Flask backend.

## 🏗️ Architecture

- **Frontend**: React with simple CSS styling
- **Backend**: Flask with basic API endpoints
- **Containerization**: Docker & Docker Compose

## 📊 Analysis Types

The application supports 6 professional financial valuation methods:

1. **DCF Valuation (WACC)** - Standard discounted cash flow using weighted average cost of capital
2. **APV Valuation** - Adjusted Present Value method separating unlevered value from financing effects
3. **Comparable Multiples** - Relative valuation using peer company ratios
4. **Scenario Analysis** - Multiple scenarios with different parameter combinations
5. **Sensitivity Analysis** - Parameter impact analysis on key valuation drivers
6. **Monte Carlo Simulation** - Risk analysis with probability distributions

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose

### Option 1: Quick Start (Recommended)

```bash
./quick-start.sh
```

### Option 2: Manual Start

```bash
# Start the application
docker-compose up --build -d
```

### Access the Application

- **Frontend**: http://localhost:3000 (React application)
- **Backend API**: http://localhost:8000 (Flask API)
- **Backend Root**: http://localhost:8000/ (API documentation)

## 📁 Project Structure

```
financial-valuation-app/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   ├── package.json
│   └── Dockerfile
├── backend/                 # Flask backend
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── finance_core/       # Financial calculation engine
│   └── Dockerfile
├── docker-compose.yml      # Docker orchestration
├── quick-start.sh          # Quick start script
└── README.md
```

## 📱 Application Flow

### 1. Analysis Selection
- Choose one or more analysis types using checkboxes
- Visual feedback for selected analyses
- Continue button shows count of selected analyses

### 2. Input Form
- Shows all selected analyses at the top
- Single form with financial inputs (revenue, margins, WACC, etc.)
- Same inputs used for all selected analyses
- Form validation and submission

### 3. Results
- **Individual Results**: Detailed results for each analysis type
- **Comparison Summary**: Side-by-side comparison of all analyses
- **Charts**: Placeholder for comparison charts

## 🔧 Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up --build -d
```

## 📊 API Endpoints

### Analysis Management
- `GET /api/analysis/types` - Get available analysis types
- `POST /api/analysis` - Create new analysis

### Valuation Processing
- `POST /api/valuation/{id}/inputs` - Submit input data

### Results
- `GET /api/results/{id}/results` - Get analysis results
- `GET /api/results/{id}/status` - Get processing status

## 🚀 Next Steps

1. **Start the application** using the quick start script
2. **Access the frontend** at http://localhost:3000
3. **Select an analysis type** from the 6 available options
4. **Fill in the input form** with your financial data
5. **View the results** with comprehensive analysis

## 🔮 Future Enhancements

- [ ] Real-time charts with Recharts
- [ ] PDF report generation
- [ ] Excel export functionality
- [ ] User authentication
- [ ] Advanced charting options
- [ ] Mobile responsive design

## 🆘 Troubleshooting

If you encounter issues:

1. **Check logs**: `docker-compose logs -f`
2. **Restart services**: `docker-compose restart`
3. **Rebuild containers**: `docker-compose up --build -d`
4. **Check Docker status**: `docker ps`

## 📄 License

This project is licensed under the MIT License. 