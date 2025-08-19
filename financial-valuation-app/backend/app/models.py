from app import db, ma
from datetime import datetime
import json

class Analysis(db.Model):
    """Model for storing analysis metadata"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # dcf_wacc, apv, multiples, scenario, sensitivity, monte_carlo
    company_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    task_id = db.Column(db.String(255), nullable=True)  # Celery task ID for status tracking
    
    # Relationships
    inputs = db.relationship('AnalysisInput', backref='analysis', uselist=False, cascade='all, delete-orphan')
    results = db.relationship('AnalysisResult', backref='analysis', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Analysis {self.name} - {self.analysis_type}>'

class AnalysisInput(db.Model):
    """Model for storing analysis input data"""
    __tablename__ = 'analysis_inputs'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    
    # Financial inputs (stored as JSON)
    financial_inputs = db.Column(db.JSON, nullable=False)
    
    # Analysis-specific inputs
    comparable_multiples = db.Column(db.JSON, nullable=True)
    scenarios = db.Column(db.JSON, nullable=True)
    sensitivity_analysis = db.Column(db.JSON, nullable=True)
    monte_carlo_specs = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnalysisInput {self.analysis_id}>'

class AnalysisResult(db.Model):
    """Model for storing analysis results"""
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    
    # Results data (stored as JSON)
    results_data = db.Column(db.JSON, nullable=False)
    
    # Summary metrics
    enterprise_value = db.Column(db.Float, nullable=True)
    equity_value = db.Column(db.Float, nullable=True)
    price_per_share = db.Column(db.Float, nullable=True)
    
    # Error information
    error_message = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnalysisResult {self.analysis_id}>'

# Marshmallow schemas for serialization
class AnalysisSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Analysis
    
    id = ma.auto_field()
    name = ma.auto_field()
    analysis_type = ma.auto_field()
    company_name = ma.auto_field()
    created_at = ma.auto_field()
    updated_at = ma.auto_field()
    status = ma.auto_field()

class AnalysisInputSchema(ma.SQLAlchemySchema):
    class Meta:
        model = AnalysisInput
    
    id = ma.auto_field()
    analysis_id = ma.auto_field()
    financial_inputs = ma.auto_field()
    comparable_multiples = ma.auto_field()
    scenarios = ma.auto_field()
    sensitivity_analysis = ma.auto_field()
    monte_carlo_specs = ma.auto_field()
    created_at = ma.auto_field()

class AnalysisResultSchema(ma.SQLAlchemySchema):
    class Meta:
        model = AnalysisResult
    
    id = ma.auto_field()
    analysis_id = ma.auto_field()
    results_data = ma.auto_field()
    enterprise_value = ma.auto_field()
    equity_value = ma.auto_field()
    price_per_share = ma.auto_field()
    error_message = ma.auto_field()
    created_at = ma.auto_field()

# Initialize schemas
analysis_schema = AnalysisSchema()
analyses_schema = AnalysisSchema(many=True)
analysis_input_schema = AnalysisInputSchema()
analysis_result_schema = AnalysisResultSchema() 