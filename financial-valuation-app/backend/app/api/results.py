from flask import Blueprint, request, jsonify
from app import db
from app.models import Analysis, AnalysisResult, analysis_result_schema
import json

results_bp = Blueprint('results', __name__)

@results_bp.route('/<int:analysis_id>/results', methods=['GET'])
def get_results(analysis_id):
    """Get results for analysis"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        result = AnalysisResult.query.filter_by(analysis_id=analysis_id).first()
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'No results found for this analysis'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'analysis': {
                    'id': analysis.id,
                    'name': analysis.name,
                    'analysis_type': analysis.analysis_type,
                    'company_name': analysis.company_name,
                    'status': analysis.status,
                    'created_at': analysis.created_at.isoformat()
                },
                'results': analysis_result_schema.dump(result)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@results_bp.route('/<int:analysis_id>/status', methods=['GET'])
def get_analysis_status(analysis_id):
    """Get analysis status and task information"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        result = AnalysisResult.query.filter_by(analysis_id=analysis_id).first()
        
        response_data = {
            'analysis_id': analysis.id,
            'status': analysis.status,
            'created_at': analysis.created_at.isoformat(),
            'updated_at': analysis.updated_at.isoformat()
        }
        
        if result:
            response_data['has_results'] = True
            response_data['results_summary'] = {
                'enterprise_value': result.enterprise_value,
                'equity_value': result.equity_value,
                'price_per_share': result.price_per_share
            }
        else:
            response_data['has_results'] = False
        
        return jsonify({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@results_bp.route('/<int:analysis_id>/results/summary', methods=['GET'])
def get_results_summary(analysis_id):
    """Get summary of results"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        result = AnalysisResult.query.filter_by(analysis_id=analysis_id).first()
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'No results found for this analysis'
            }), 404
        
        # Extract summary based on analysis type
        summary = {
            'analysis_type': analysis.analysis_type,
            'company_name': analysis.company_name,
            'enterprise_value': result.enterprise_value,
            'equity_value': result.equity_value,
            'price_per_share': result.price_per_share
        }
        
        # Add analysis-specific summary
        results_data = result.results_data
        
        if analysis.analysis_type == 'dcf_wacc':
            if 'dcf_wacc' in results_data:
                dcf_data = results_data['dcf_wacc']
                summary.update({
                    'wacc': dcf_data.get('wacc'),
                    'terminal_value': dcf_data.get('terminal_value'),
                    'free_cash_flows': dcf_data.get('free_cash_flows')
                })
        
        elif analysis.analysis_type == 'apv':
            if 'apv' in results_data:
                apv_data = results_data['apv']
                summary.update({
                    'unlevered_enterprise_value': apv_data.get('unlevered_enterprise_value'),
                    'pv_tax_shields': apv_data.get('pv_tax_shields'),
                    'apv_enterprise_value': apv_data.get('apv_enterprise_value')
                })
        
        elif analysis.analysis_type == 'multiples':
            if 'comparable_multiples' in results_data:
                multiples_data = results_data['comparable_multiples']
                summary.update({
                    'implied_values': multiples_data.get('implied_values'),
                    'mean_enterprise_value': multiples_data.get('mean_enterprise_value'),
                    'median_enterprise_value': multiples_data.get('median_enterprise_value')
                })
        
        elif analysis.analysis_type == 'scenario':
            if 'scenarios' in results_data:
                scenarios_data = results_data['scenarios']
                summary.update({
                    'scenario_results': scenarios_data.get('scenarios'),
                    'base_case_enterprise_value': scenarios_data.get('base_case', {}).get('enterprise_value')
                })
        
        elif analysis.analysis_type == 'sensitivity':
            if 'sensitivity_analysis' in results_data:
                sensitivity_data = results_data['sensitivity_analysis']
                summary.update({
                    'wacc_sensitivity': sensitivity_data.get('wacc_sensitivity'),
                    'ebit_margin_sensitivity': sensitivity_data.get('ebit_margin_sensitivity'),
                    'terminal_growth_sensitivity': sensitivity_data.get('terminal_growth_sensitivity')
                })
        
        elif analysis.analysis_type == 'monte_carlo':
            if 'monte_carlo' in results_data:
                mc_data = results_data['monte_carlo']
                summary.update({
                    'mean_enterprise_value': mc_data.get('enterprise_value', {}).get('mean'),
                    'median_enterprise_value': mc_data.get('enterprise_value', {}).get('median'),
                    'confidence_interval_95': {
                        'lower': mc_data.get('enterprise_value', {}).get('p5'),
                        'upper': mc_data.get('enterprise_value', {}).get('p95')
                    }
                })
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@results_bp.route('/<int:analysis_id>/results/export', methods=['GET'])
def export_results(analysis_id):
    """Export results in various formats"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        result = AnalysisResult.query.filter_by(analysis_id=analysis_id).first()
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'No results found for this analysis'
            }), 404
        
        format_type = request.args.get('format', 'json')
        
        if format_type == 'json':
            export_data = {
                'analysis': {
                    'id': analysis.id,
                    'name': analysis.name,
                    'analysis_type': analysis.analysis_type,
                    'company_name': analysis.company_name,
                    'created_at': analysis.created_at.isoformat()
                },
                'results': result.results_data,
                'summary': {
                    'enterprise_value': result.enterprise_value,
                    'equity_value': result.equity_value,
                    'price_per_share': result.price_per_share
                }
            }
            
            return jsonify({
                'success': True,
                'data': export_data,
                'format': 'json'
            })
        
        elif format_type == 'csv':
            # TODO: Implement CSV export
            return jsonify({
                'success': False,
                'error': 'CSV export not yet implemented'
            }), 501
        
        elif format_type == 'pdf':
            # TODO: Implement PDF export
            return jsonify({
                'success': False,
                'error': 'PDF export not yet implemented'
            }), 501
        
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported format: {format_type}'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@results_bp.route('/<int:analysis_id>/results', methods=['DELETE'])
def delete_results(analysis_id):
    """Delete results for analysis"""
    try:
        result = AnalysisResult.query.filter_by(analysis_id=analysis_id).first()
        if not result:
            return jsonify({
                'success': False,
                'error': 'No results found for this analysis'
            }), 404
        
        db.session.delete(result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Results deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 