from celery import Celery
from app import create_app, db
from app.models import Analysis, AnalysisInput, AnalysisResult
from app.services.finance_core_service import FinanceCoreService
import os

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
)

@celery.task(bind=True)
def run_valuation_task(self, analysis_id):
    """Background task to run valuation analysis"""
    try:
        # Create Flask app context
        app = create_app()
        with app.app_context():
            # Get analysis and inputs
            analysis = Analysis.query.get(analysis_id)
            if not analysis:
                self.update_state(state='FAILURE', meta={'error': 'Analysis not found'})
                return {'success': False, 'error': 'Analysis not found'}
            
            analysis_input = AnalysisInput.query.filter_by(analysis_id=analysis_id).first()
            if not analysis_input:
                self.update_state(state='FAILURE', meta={'error': 'Analysis inputs not found'})
                return {'success': False, 'error': 'Analysis inputs not found'}
            
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
            results = finance_service.run_analysis(
                analysis.analysis_type,
                inputs,
                analysis.company_name
            )
            
            if not results['success']:
                # Update analysis status to failed
                analysis.status = 'failed'
                db.session.commit()
                
                self.update_state(state='FAILURE', meta={'error': results['error']})
                return {'success': False, 'error': results['error']}
            
            # Save results
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
            
            self.update_state(state='SUCCESS', meta={'status': 'Analysis completed'})
            
            return {
                'success': True,
                'analysis_id': analysis_id,
                'enterprise_value': results.get('enterprise_value'),
                'equity_value': results.get('equity_value'),
                'price_per_share': results.get('price_per_share')
            }
    
    except Exception as e:
        # Update analysis status to failed
        try:
            analysis = Analysis.query.get(analysis_id)
            if analysis:
                analysis.status = 'failed'
                db.session.commit()
        except:
            pass
        
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'success': False, 'error': str(e)}

def get_task_status(analysis_id):
    """Get task status for analysis"""
    try:
        # Find the task for this analysis
        # This is a simplified implementation - in production you'd want to store task IDs
        task_id = f"run_valuation_task_{analysis_id}"
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