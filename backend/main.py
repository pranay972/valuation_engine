from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import json
import io
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import sys
import os
import tempfile
import shutil
import traceback
import numpy as np

# Handle imports for both module and direct execution
try:
    from .services.valuation_service import valuation_service
    from .utils.exceptions import ValuationError, InvalidInputError, CalculationError, DataValidationError
    from .config.logging import get_logger, setup_logging
except ImportError:
    # When running directly, use absolute imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backend.services.valuation_service import valuation_service
    from backend.utils.exceptions import ValuationError, InvalidInputError, CalculationError, DataValidationError
    from backend.config.logging import get_logger, setup_logging

# Setup logging for API
logger = get_logger(__name__)

app = FastAPI(
    title="Financial Valuation API",
    description="API for financial valuation calculations including DCF, Monte Carlo, Multiples, and more",
    version="2.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store uploaded files temporarily
uploaded_files = {}

# Pydantic models for request/response
class ValuationRequest(BaseModel):
    # Financial projections
    revenue: Optional[List[float]] = None
    ebit_margin: float = 0.20
    capex: Optional[List[float]] = None
    depreciation: Optional[List[float]] = None
    nwc_changes: Optional[List[float]] = None
    fcf_series: Optional[List[float]] = None
    
    # Valuation assumptions
    terminal_growth: float = 0.02
    wacc: float = 0.10
    tax_rate: float = 0.21
    mid_year_convention: bool = False
    share_count: float = 100000000.0
    cost_of_debt: float = 0.05
    debt_schedule: Dict[int, float] = {}
    
    # Analysis types
    analyses: List[str] = ["WACC DCF"]
    mc_runs: int = 2000
    variable_specs: Dict[str, Any] = {}
    scenarios: Dict[str, Any] = {}
    sensitivity_ranges: Dict[str, Any] = {}
    comps_data: Optional[List[Dict[str, Any]]] = None

class ValuationResponse(BaseModel):
    success: bool
    results: Dict[str, Any]
    message: str = ""

@app.get("/")
async def root():
    return {"message": "Financial Valuation API is running"}

@app.post("/api/valuate", response_model=ValuationResponse)
async def run_valuation(request: ValuationRequest):
    """Run valuation analysis based on provided parameters"""
    try:
        logger.info(f"Received valuation request with analyses: {request.analyses}")
        
        # Validate that if sensitivity analysis is selected, ranges are provided
        if "Sensitivity" in request.analyses and not request.sensitivity_ranges:
            raise InvalidInputError(
                "Sensitivity analysis selected but no sensitivity ranges provided. Please configure sensitivity parameters in the Advanced Analysis section.",
                field="sensitivity_ranges"
            )
        
        # Convert request to dictionary for service layer
        input_data = {
            'revenue': request.revenue,
            'ebit_margin': request.ebit_margin,
            'capex': request.capex,
            'depreciation': request.depreciation,
            'nwc_changes': request.nwc_changes,
            'fcf_series': request.fcf_series,
            'terminal_growth': request.terminal_growth,
            'wacc': request.wacc,
            'tax_rate': request.tax_rate,
            'mid_year_convention': request.mid_year_convention,
            'share_count': request.share_count,
            'cost_of_debt': request.cost_of_debt,
            'debt_schedule': request.debt_schedule,
            'variable_specs': request.variable_specs,
            'scenarios': request.scenarios,
            'sensitivity_ranges': request.sensitivity_ranges,
            'comps_data': request.comps_data
        }
        
        # Use service layer for validation and processing
        try:
            validated_data = valuation_service.validate_input_data(input_data)
            params = valuation_service.create_valuation_params(validated_data)
            results = valuation_service.run_valuation_analyses(
                params, 
                request.analyses, 
                comps_data=request.comps_data,
                mc_runs=request.mc_runs
            )
            
            return ValuationResponse(
                success=True,
                results=results,
                message="Valuation completed successfully"
            )
            
        except (InvalidInputError, DataValidationError) as e:
            logger.warning(f"Input validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except CalculationError as e:
            logger.error(f"Calculation failed: {str(e)}")
            raise HTTPException(status_code=422, detail=str(e))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in valuation endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/upload-comps")
async def upload_comps(file: UploadFile = File(...)):
    """Upload comparable companies CSV file"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read CSV content
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # Validate CSV structure (basic check)
        required_columns = ['Company', 'EV/EBITDA', 'P/E', 'Revenue']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Return preview of data
        return {
            "success": True,
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head().to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 