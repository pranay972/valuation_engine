from celery import Celery
from app import create_app, db
from app.models import Analysis, AnalysisInput, AnalysisResult
from app.services.finance_core_service import FinanceCoreService
import os
import logging
import traceback

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
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
    worker_max_tasks_per_child=1,  # Restart worker after each task to prevent state corruption
    worker_max_memory_per_child=100000,  # Restart worker if memory usage exceeds 100MB
    worker_restart_strategy='restart',  # Explicitly set restart strategy
    worker_pool_restarts=True,  # Enable worker pool restarts
)

@celery.task(bind=True)
def run_valuation_task(self, analysis_id):
    """Background task to run valuation analysis"""
    logger.info(f"Starting valuation task for analysis ID: {analysis_id}")
    
    # Check if we're running in a proper Celery context
    is_celery_context = hasattr(self, 'request') and self.request and self.request.id
    
    try:
        # Create Flask app context
        app = create_app()
        with app.app_context():
            # Get analysis and inputs
            logger.info(f"Fetching analysis data for ID: {analysis_id}")
            analysis = Analysis.query.get(analysis_id)
            if not analysis:
                error_msg = 'Analysis not found'
                logger.error(f"{error_msg} for ID: {analysis_id}")
                if is_celery_context:
                    self.update_state(state='FAILURE', meta={'error': error_msg})
                return {'success': False, 'error': error_msg}
            
            logger.info(f"Analysis found: {analysis.name} ({analysis.analysis_type}) for {analysis.company_name}")
            
            analysis_input = AnalysisInput.query.filter_by(analysis_id=analysis_id).first()
            if not analysis_input:
                error_msg = 'Analysis inputs not found'
                logger.error(f"{error_msg} for analysis ID: {analysis_id}")
                if is_celery_context:
                    self.update_state(state='FAILURE', meta={'error': error_msg})
                return {'success': False, 'error': error_msg}
            
            logger.info(f"Analysis inputs found with {len(analysis_input.financial_inputs)} financial fields")
            
            # Update task state
            if is_celery_context:
                self.update_state(state='PROGRESS', meta={'status': 'Starting analysis'})
            
            # Prepare inputs for finance core
            inputs = {
                'financial_inputs': analysis_input.financial_inputs,
                'comparable_multiples': analysis_input.comparable_multiples,
                'scenarios': analysis_input.scenarios,
                'sensitivity_analysis': analysis_input.sensitivity_analysis,
                'monte_carlo_specs': analysis_input.monte_carlo_specs
            }
            
            logger.info(f"Prepared inputs for {analysis.analysis_type} analysis")
            
            # Run analysis
            if is_celery_context:
                self.update_state(state='PROGRESS', meta={'status': 'Running analysis'})
            
            # Create a fresh FinanceCoreService instance for each task to prevent state corruption
            logger.info("Creating fresh FinanceCoreService instance...")
            try:
                finance_service = FinanceCoreService()
                logger.info(f"FinanceCoreService created successfully. Calculator available: {finance_service.calculator is not None}")
                
                if not finance_service.calculator:
                    error_msg = 'Finance calculator not available in service'
                    logger.error(error_msg)
                    analysis.status = 'failed'
                    db.session.commit()
                    if is_celery_context:
                        self.update_state(state='FAILURE', meta={'error': error_msg})
                    return {'success': False, 'error': error_msg}
                
                logger.info("Finance calculator is available and ready")
            except Exception as e:
                error_msg = f'Error creating FinanceCoreService: {str(e)}'
                logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
                analysis.status = 'failed'
                db.session.commit()
                if is_celery_context:
                    self.update_state(state='FAILURE', meta={'error': error_msg})
                return {'success': False, 'error': error_msg}
            
            logger.info(f"Executing {analysis.analysis_type} analysis...")
            results = finance_service.run_analysis(
                analysis.analysis_type,
                inputs,
                analysis.company_name
            )
            
            logger.info(f"Analysis execution completed. Success: {results.get('success')}")
            
            if not results['success']:
                error_msg = results.get('error', 'Unknown error')
                error_type = results.get('error_type', 'unknown')
                logger.error(f"Analysis failed with error type '{error_type}': {error_msg}")
                
                # Log additional error details if available
                if 'validation_errors' in results:
                    logger.error(f"Validation errors: {results['validation_errors']}")
                if 'exception_details' in results:
                    logger.error(f"Exception details: {results['exception_details']}")
                if 'traceback' in results:
                    logger.error(f"Full traceback: {results['traceback']}")
                
                # Update analysis status to failed
                analysis.status = 'failed'
                db.session.commit()
                
                if is_celery_context:
                    self.update_state(state='FAILURE', meta={
                        'error': error_msg,
                        'error_type': error_type,
                        'validation_errors': results.get('validation_errors'),
                        'exception_details': results.get('exception_details')
                    })
                return {'success': False, 'error': error_msg, 'error_type': error_type}
            
            # Save results
            if is_celery_context:
                self.update_state(state='PROGRESS', meta={'status': 'Saving results'})
            
            # Check if results already exist
            existing_result = AnalysisResult.query.filter_by(analysis_id=analysis_id).first()
            if existing_result:
                existing_result.results_data = results['results']
                existing_result.enterprise_value = results.get('enterprise_value')
                existing_result.equity_value = results.get('equity_value')
                existing_result.price_per_share = results.get('price_per_share')
                existing_result.error_message = None
                result = existing_result
            else:
                result = AnalysisResult(
                    analysis_id=analysis_id,
                    results_data=results['results'],
                    enterprise_value=results.get('enterprise_value'),
                    equity_value=results.get('equity_value'),
                    price_per_share=results.get('price_per_share')
                )
                db.session.add(result)
            
            # Update analysis status
            analysis.status = 'completed'
            db.session.commit()
            
            logger.info(f"Analysis {analysis_id} completed successfully")
            if is_celery_context:
                self.update_state(state='SUCCESS', meta={'status': 'Analysis completed'})
            
            return {
                'success': True,
                'analysis_id': analysis_id,
                'enterprise_value': results.get('enterprise_value'),
                'equity_value': results.get('equity_value'),
                'price_per_share': results.get('price_per_share')
            }
    
    except Exception as e:
        error_msg = f'Unexpected error in valuation task: {str(e)}'
        logger.error(f"{error_msg}\nTraceback: {traceback.format_exc()}")
        
        # Update analysis status to failed
        try:
            analysis = Analysis.query.get(analysis_id)
            if analysis:
                analysis.status = 'failed'
                db.session.commit()
                logger.info(f"Updated analysis {analysis_id} status to failed")
        except Exception as db_error:
            logger.error(f"Failed to update analysis status: {db_error}")
        
        if is_celery_context:
            self.update_state(state='FAILURE', meta={'error': error_msg, 'traceback': traceback.format_exc()})
        return {'success': False, 'error': error_msg}

def get_task_status(analysis_id):
    """Get task status for analysis"""
    try:
        # Get the analysis to find the stored task ID
        app = create_app()
        with app.app_context():
            analysis = Analysis.query.get(analysis_id)
            if not analysis or not analysis.task_id:
                return {
                    'state': 'UNKNOWN',
                    'status': 'No task ID found for this analysis'
                }
            
            task_id = analysis.task_id
            task = run_valuation_task.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            return {
                'state': 'PENDING',
                'status': 'Task is waiting for execution'
            }
        elif task.state == 'PROGRESS':
            return {
                'state': 'PROGRESS',
                'status': task.info.get('status', 'Processing...')
            }
        elif task.state == 'SUCCESS':
            return {
                'state': 'SUCCESS',
                'status': 'Analysis completed successfully'
            }
        elif task.state == 'FAILURE':
            return {
                'state': 'FAILURE',
                'status': 'Analysis failed',
                'error': task.info.get('error', 'Unknown error')
            }
        else:
            return {
                'state': task.state,
                'status': 'Unknown state'
            }
    except Exception as e:
        return {
            'state': 'ERROR',
            'status': f'Error getting task status: {str(e)}'
        } 