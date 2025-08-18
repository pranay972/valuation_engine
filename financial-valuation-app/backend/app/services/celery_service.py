from celery import Celery
from app import create_app, db
from app.models import Analysis, AnalysisInput, AnalysisResult
from app.services.finance_core_service import FinanceCoreService
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery instance
celery = Celery('financial_valuation')

# Configure Celery
celery.conf.update(
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

@celery.task(bind=True)
def run_valuation_task(self, analysis_id):
    """Background task to run valuation analysis"""
    logger.info(f"Starting valuation task for analysis ID: {analysis_id}")
    
    try:
        # Create Flask app context
        app = create_app()
        with app.app_context():
            # Get analysis and inputs
            analysis = Analysis.query.get(analysis_id)
            if not analysis:
                error_msg = 'Analysis not found'
                logger.error(f"{error_msg} for ID: {analysis_id}")
                return {'success': False, 'error': error_msg}
            
            analysis_input = AnalysisInput.query.filter_by(analysis_id=analysis_id).first()
            if not analysis_input:
                error_msg = 'Analysis inputs not found'
                logger.error(f"{error_msg} for analysis ID: {analysis_id}")
                return {'success': False, 'error': error_msg}
            
            # Update task state
            self.update_state(state='PROGRESS', meta={'status': 'Starting analysis'})
            
            # Prepare inputs for finance core
            inputs = {
                'financial_inputs': analysis_input.financial_inputs,
                'comparable_multiples': analysis_input.comparable_multiples,
                'scenarios': analysis_input.scenarios,
                'sensitivity_analysis': analysis_input.sensitivity_analysis,
                'monte_carlo_specs': analysis_input.monte_carlo_specs
            }
            
            # Run analysis
            self.update_state(state='PROGRESS', meta={'status': 'Running analysis'})
            
            finance_service = FinanceCoreService()
            if not finance_service.calculator:
                error_msg = 'Finance calculator not available'
                logger.error(error_msg)
                analysis.status = 'failed'
                db.session.commit()
                return {'success': False, 'error': error_msg}
            
            # Run the analysis
            results = finance_service.run_analysis(
                analysis.analysis_type,
                inputs,
                analysis.company_name
            )
            
            if results['success']:
                # Store results
                analysis_result = AnalysisResult(
                    analysis_id=analysis_id,
                    results_data=results['results']
                )
                db.session.add(analysis_result)
                analysis.status = 'completed'
                db.session.commit()
                
                logger.info(f"Analysis completed successfully for {analysis.company_name}")
                return {'success': True, 'results': results['results']}
            else:
                # Analysis failed
                analysis.status = 'failed'
                db.session.commit()
                logger.error(f"Analysis failed: {results.get('error', 'Unknown error')}")
                return {'success': False, 'error': results.get('error', 'Unknown error')}
                
    except Exception as e:
        logger.error(f"Task failed: {str(e)}", exc_info=True)
        
        # Update analysis status to failed
        try:
            with app.app_context():
                analysis = Analysis.query.get(analysis_id)
                if analysis:
                    analysis.status = 'failed'
                    db.session.commit()
        except:
            pass
        
        return {'success': False, 'error': str(e)} 