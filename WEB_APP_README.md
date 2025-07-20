# Financial Valuation Web Application

A modern web application for financial valuation analysis, built with React frontend and FastAPI backend.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation & Running

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <your-repo-url>
   cd valuation
   ```

2. **Start the application**:
   ```bash
   python start_app.py
   ```

   This will:
   - Install all dependencies automatically
   - Start the FastAPI backend on http://localhost:8000
   - Start the React frontend on http://localhost:3000
   - Open your browser to the application

3. **Access the application**:
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
valuation/
├── api/                    # FastAPI backend
│   ├── main.py            # API server
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── form/      # Form components
│   │   │   ├── Header.js
│   │   │   ├── ValuationForm.js
│   │   │   └── Results.js
│   │   └── App.js
│   └── package.json
├── start_app.py           # Startup script
├── app.py                 # Original Streamlit app
└── [other valuation files]
```

## 🔧 Manual Setup (Alternative)

If you prefer to run services separately:

### Backend (FastAPI)
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

## 🎯 Features

### Analysis Types
- **WACC DCF**: Standard discounted cash flow analysis
- **APV DCF**: Adjusted present value method
- **Monte Carlo**: Uncertainty analysis with probability distributions
- **Comparable Multiples**: Peer company analysis
- **Scenario Analysis**: What-if scenario testing
- **Sensitivity Analysis**: Parameter impact assessment

### Input Methods
- **Driver-based**: Enter revenue and financial drivers
- **Direct FCF**: Enter free cash flows directly

### Professional UI
- Modern Material-UI design
- Responsive layout
- Interactive forms and charts
- Professional styling

## 🌐 Deployment

### Frontend Deployment (Vercel/Netlify)
1. Build the React app:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy to Vercel:
   ```bash
   npm install -g vercel
   vercel
   ```

3. Deploy to Netlify:
   - Drag the `build` folder to Netlify
   - Or use Netlify CLI

### Backend Deployment (Railway/Render/Heroku)
1. Create a `Procfile` in the `api` directory:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. Deploy to Railway:
   - Connect your GitHub repo
   - Set the root directory to `api`
   - Deploy

3. Deploy to Render:
   - Create a new Web Service
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🔗 API Endpoints

- `GET /`: Health check
- `POST /api/valuate`: Run valuation analysis
- `POST /api/upload-comps`: Upload comparable companies CSV

## 📊 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🛠️ Development

### Adding New Features
1. **Backend**: Add new endpoints in `api/main.py`
2. **Frontend**: Add new components in `frontend/src/components/`

### Styling
- Uses Material-UI theme system
- Custom theme defined in `App.js`
- Responsive design with Grid system

### State Management
- React hooks for local state
- Form data managed in `ValuationForm.js`
- Results passed via props to `Results.js`

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**:
   - Kill existing processes: `lsof -ti:8000 | xargs kill -9`
   - Or change ports in the startup script

2. **Node.js not found**:
   - Install Node.js from https://nodejs.org/

3. **Python dependencies missing**:
   - Run: `pip install -r api/requirements.txt`

4. **Frontend build errors**:
   - Clear node_modules: `rm -rf frontend/node_modules && npm install`

## 📝 License

Same as the original project.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This web application maintains the same functionality as the original Streamlit app but with a modern, professional web interface that can be easily deployed and hosted. 