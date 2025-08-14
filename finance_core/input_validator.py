"""Input validation for financial valuation data."""

from typing import Dict, List, Any, Tuple
import warnings

class InputValidator:
    """Comprehensive input validator for financial valuation data."""
    
    @staticmethod
    def validate_financial_inputs(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate financial inputs for reasonableness and completeness.
        
        Args:
            data: Dictionary containing financial inputs
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Extract financial inputs
        financial_data = data.get('financial_inputs', data)
        
        # 1. Basic data validation
        warnings.extend(InputValidator._validate_basic_data(financial_data))
        
        # 2. Revenue projections validation
        warnings.extend(InputValidator._validate_revenue_projections(financial_data))
        
        # 3. Margin and profitability validation
        warnings.extend(InputValidator._validate_margins(financial_data))
        
        # 4. Capital structure validation
        warnings.extend(InputValidator._validate_capital_structure(financial_data))
        
        # 5. Growth and terminal value validation
        warnings.extend(InputValidator._validate_growth_assumptions(financial_data))
        
        # 6. Working capital validation
        warnings.extend(InputValidator._validate_working_capital(financial_data))
        
        # 7. Comparable multiples validation
        if 'comparable_multiples' in data:
            warnings.extend(InputValidator._validate_comparable_multiples(data['comparable_multiples']))
        
        # 8. Scenario analysis validation
        if 'scenarios' in data:
            warnings.extend(InputValidator._validate_scenarios(data['scenarios']))
        
        # 9. Monte Carlo validation
        if 'monte_carlo_specs' in data:
            warnings.extend(InputValidator._validate_monte_carlo(data['monte_carlo_specs']))
        
        # 10. Sensitivity analysis validation
        if 'sensitivity_analysis' in data:
            warnings.extend(InputValidator._validate_sensitivity_analysis(data['sensitivity_analysis']))
        
        return len(warnings) == 0, warnings
    
    @staticmethod
    def _validate_basic_data(data: Dict[str, Any]) -> List[str]:
        """Validate basic data completeness and types."""
        warnings = []
        
        required_fields = [
            'revenue', 'ebit_margin', 'tax_rate', 'capex', 'depreciation', 
            'nwc_changes', 'weighted_average_cost_of_capital', 'terminal_growth_rate',
            'share_count', 'cost_of_debt'
        ]
        
        for field in required_fields:
            if field not in data:
                warnings.append(f"Missing required field: {field}")
            elif data[field] is None:
                warnings.append(f"Required field is None: {field}")
        
        return warnings
    
    @staticmethod
    def _validate_revenue_projections(data: Dict[str, Any]) -> List[str]:
        """Validate revenue projections for reasonableness."""
        warnings = []
        
        revenue = data.get('revenue', [])
        if not isinstance(revenue, list) or len(revenue) == 0:
            warnings.append("Revenue projections must be a non-empty list")
            return warnings
        
        # Check for negative revenue
        for i, rev in enumerate(revenue):
            if rev <= 0:
                warnings.append(f"Revenue Year {i+1} must be positive: {rev}")
        
        # Check for reasonable growth rates
        for i in range(1, len(revenue)):
            growth_rate = (revenue[i] - revenue[i-1]) / revenue[i-1]
            if growth_rate > 0.5:  # 50% growth
                warnings.append(f"High revenue growth rate in Year {i+1}: {growth_rate:.1%}")
            elif growth_rate < -0.3:  # -30% decline
                warnings.append(f"Large revenue decline in Year {i+1}: {growth_rate:.1%}")
        
        return warnings
    
    @staticmethod
    def _validate_margins(data: Dict[str, Any]) -> List[str]:
        """Validate margin assumptions."""
        warnings = []
        
        ebit_margin = data.get('ebit_margin', 0)
        if ebit_margin <= 0 or ebit_margin > 0.5:
            warnings.append(f"EBIT margin seems unreasonable: {ebit_margin:.1%}")
        
        tax_rate = data.get('tax_rate', 0)
        if tax_rate < 0.15 or tax_rate > 0.35:
            warnings.append(f"Tax rate seems unreasonable: {tax_rate:.1%}")
        
        return warnings
    
    @staticmethod
    def _validate_capital_structure(data: Dict[str, Any]) -> List[str]:
        """Validate capital structure assumptions."""
        warnings = []
        
        wacc = data.get('weighted_average_cost_of_capital', 0)
        if wacc < 0.05 or wacc > 0.25:
            warnings.append(f"WACC seems unreasonable: {wacc:.1%}")
        
        cost_of_debt = data.get('cost_of_debt', 0)
        if cost_of_debt < 0.02 or cost_of_debt > 0.15:
            warnings.append(f"Cost of debt seems unreasonable: {cost_of_debt:.1%}")
        
        # Check WACC vs cost of debt
        if wacc <= cost_of_debt:
            warnings.append(f"WACC ({wacc:.1%}) should be higher than cost of debt ({cost_of_debt:.1%})")
        
        return warnings
    
    @staticmethod
    def _validate_growth_assumptions(data: Dict[str, Any]) -> List[str]:
        """Validate growth and terminal value assumptions."""
        warnings = []
        
        terminal_growth = data.get('terminal_growth_rate', 0)
        wacc = data.get('weighted_average_cost_of_capital', 0)
        
        if terminal_growth < 0:
            warnings.append(f"Terminal growth rate should be non-negative: {terminal_growth:.1%}")
        
        if terminal_growth > 0.05:
            warnings.append(f"Terminal growth rate seems high: {terminal_growth:.1%}")
        
        if terminal_growth >= wacc:
            warnings.append(f"Terminal growth ({terminal_growth:.1%}) must be less than WACC ({wacc:.1%})")
        
        return warnings
    
    @staticmethod
    def _validate_working_capital(data: Dict[str, Any]) -> List[str]:
        """Validate working capital assumptions."""
        warnings = []
        
        nwc_changes = data.get('nwc_changes', [])
        revenue = data.get('revenue', [])
        
        if len(nwc_changes) != len(revenue):
            warnings.append("NWC changes must have same length as revenue projections")
            return warnings
        
        # Check NWC changes as percentage of revenue
        for i, nwc_change in enumerate(nwc_changes):
            if revenue[i] > 0:
                nwc_ratio = abs(nwc_change) / revenue[i]
                if nwc_ratio > 0.15:  # 15% of revenue
                    warnings.append(f"Large NWC change in Year {i+1}: {nwc_ratio:.1%} of revenue")
        
        return warnings
    
    @staticmethod
    def _validate_comparable_multiples(multiples: Dict[str, List[float]]) -> List[str]:
        """Validate comparable company multiples."""
        warnings = []
        
        for multiple_type, values in multiples.items():
            if not isinstance(values, list) or len(values) == 0:
                warnings.append(f"Comparable multiples for {multiple_type} must be non-empty list")
                continue
            
            # Check for reasonable multiple ranges
            for i, value in enumerate(values):
                if value <= 0:
                    warnings.append(f"Multiple {multiple_type} #{i+1} must be positive: {value}")
                elif value > 100:  # Very high multiple
                    warnings.append(f"Very high multiple {multiple_type} #{i+1}: {value}")
        
        return warnings
    
    @staticmethod
    def _validate_scenarios(scenarios: Dict[str, Dict[str, Any]]) -> List[str]:
        """Validate scenario analysis inputs."""
        warnings = []
        
        for scenario_name, scenario_data in scenarios.items():
            if not isinstance(scenario_data, dict):
                warnings.append(f"Scenario {scenario_name} must be a dictionary")
                continue
            
            # Validate scenario parameters
            for param, value in scenario_data.items():
                if param == 'ebit_margin' and (value <= 0 or value > 0.5):
                    warnings.append(f"Scenario {scenario_name} EBIT margin seems unreasonable: {value:.1%}")
                elif param == 'terminal_growth_rate' and (value < 0 or value > 0.05):
                    warnings.append(f"Scenario {scenario_name} terminal growth seems unreasonable: {value:.1%}")
                elif param == 'weighted_average_cost_of_capital' and (value < 0.05 or value > 0.25):
                    warnings.append(f"Scenario {scenario_name} WACC seems unreasonable: {value:.1%}")
        
        return warnings
    
    @staticmethod
    def _validate_monte_carlo(specs: Dict[str, Dict[str, Any]]) -> List[str]:
        """Validate Monte Carlo simulation specifications."""
        warnings = []
        
        for variable, spec in specs.items():
            if not isinstance(spec, dict):
                warnings.append(f"Monte Carlo spec for {variable} must be a dictionary")
                continue
            
            distribution = spec.get('distribution')
            params = spec.get('params', {})
            
            if distribution not in ['normal', 'uniform', 'lognormal', 'triangular']:
                warnings.append(f"Unsupported distribution for {variable}: {distribution}")
            
            if distribution == 'normal':
                mean = params.get('mean')
                std = params.get('std')
                if std <= 0:
                    warnings.append(f"Standard deviation for {variable} must be positive: {std}")
                if abs(mean) > 1:
                    warnings.append(f"Mean for {variable} seems large: {mean}")
        
        return warnings
    
    @staticmethod
    def _validate_sensitivity_analysis(sensitivity: Dict[str, List[float]]) -> List[str]:
        """Validate sensitivity analysis inputs."""
        warnings = []
        
        for variable, values in sensitivity.items():
            if not isinstance(values, list) or len(values) == 0:
                warnings.append(f"Sensitivity analysis for {variable} must be non-empty list")
                continue
            
            # Check for reasonable ranges
            for i, value in enumerate(values):
                if variable == 'ebit_margin' and (value <= 0 or value > 0.5):
                    warnings.append(f"Sensitivity EBIT margin #{i+1} seems unreasonable: {value:.1%}")
                elif variable == 'terminal_growth_rate' and (value < 0 or value > 0.05):
                    warnings.append(f"Sensitivity terminal growth #{i+1} seems unreasonable: {value:.1%}")
                elif variable == 'weighted_average_cost_of_capital' and (value < 0.05 or value > 0.25):
                    warnings.append(f"Sensitivity WACC #{i+1} seems unreasonable: {value:.1%}")
        
        return warnings 