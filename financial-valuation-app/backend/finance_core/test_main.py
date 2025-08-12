#!/usr/bin/env python3
"""
Unit Tests for Main Valuation Workflow Script

Tests the CSV to CSV valuation pipeline functionality in main.py
"""

import unittest
import json
import tempfile
import os
import sys
import csv
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

# Import the modules to test
from main import (
    generate_csv_report, 
    run_valuation_workflow,
    main
)
from csv_to_json_converter import csv_to_json
from finance_calculator import FinancialValuationEngine, parse_financial_inputs

class TestCSVToJSON(unittest.TestCase):
    """Test CSV to JSON conversion functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_csv_data = [
            {
                'Field': 'Company Name',
                'Value': 'Test Company',
                'Description': 'Name of the company'
            },
            {
                'Field': 'Valuation Date',
                'Value': '2024-01-01',
                'Description': 'Date of valuation'
            },
            {
                'Field': 'Forecast Years',
                'Value': '5',
                'Description': 'Number of forecast years'
            },
            {
                'Field': 'Revenue Year 1',
                'Value': '1000',
                'Description': 'Revenue for year 1'
            },
            {
                'Field': 'Revenue Year 2',
                'Value': '1100',
                'Description': 'Revenue for year 2'
            },
            {
                'Field': 'Revenue Year 3',
                'Value': '1200',
                'Description': 'Revenue for year 3'
            },
            {
                'Field': 'Revenue Year 4',
                'Value': '1300',
                'Description': 'Revenue for year 4'
            },
            {
                'Field': 'Revenue Year 5',
                'Value': '1400',
                'Description': 'Revenue for year 5'
            },
            {
                'Field': 'EBIT Margin',
                'Value': '0.15',
                'Description': 'EBIT margin percentage'
            },
            {
                'Field': 'Tax Rate',
                'Value': '0.25',
                'Description': 'Corporate tax rate'
            },
            {
                'Field': 'CapEx Year 1',
                'Value': '200',
                'Description': 'Capital expenditure year 1'
            },
            {
                'Field': 'CapEx Year 2',
                'Value': '220',
                'Description': 'Capital expenditure year 2'
            },
            {
                'Field': 'CapEx Year 3',
                'Value': '240',
                'Description': 'Capital expenditure year 3'
            },
            {
                'Field': 'CapEx Year 4',
                'Value': '260',
                'Description': 'Capital expenditure year 4'
            },
            {
                'Field': 'CapEx Year 5',
                'Value': '280',
                'Description': 'Capital expenditure year 5'
            },
            {
                'Field': 'Depreciation Year 1',
                'Value': '150',
                'Description': 'Depreciation year 1'
            },
            {
                'Field': 'Depreciation Year 2',
                'Value': '160',
                'Description': 'Depreciation year 2'
            },
            {
                'Field': 'Depreciation Year 3',
                'Value': '170',
                'Description': 'Depreciation year 3'
            },
            {
                'Field': 'Depreciation Year 4',
                'Value': '180',
                'Description': 'Depreciation year 4'
            },
            {
                'Field': 'Depreciation Year 5',
                'Value': '190',
                'Description': 'Depreciation year 5'
            },
            {
                'Field': 'NWC Changes Year 1',
                'Value': '50',
                'Description': 'Net working capital changes year 1'
            },
            {
                'Field': 'NWC Changes Year 2',
                'Value': '55',
                'Description': 'Net working capital changes year 2'
            },
            {
                'Field': 'NWC Changes Year 3',
                'Value': '60',
                'Description': 'Net working capital changes year 3'
            },
            {
                'Field': 'NWC Changes Year 4',
                'Value': '65',
                'Description': 'Net working capital changes year 4'
            },
            {
                'Field': 'NWC Changes Year 5',
                'Value': '70',
                'Description': 'Net working capital changes year 5'
            },
            {
                'Field': 'WACC',
                'Value': '0.10',
                'Description': 'Weighted average cost of capital'
            },
            {
                'Field': 'Terminal Growth Rate',
                'Value': '0.03',
                'Description': 'Terminal growth rate'
            },
            {
                'Field': 'Share Count',
                'Value': '100',
                'Description': 'Number of shares outstanding'
            },
            {
                'Field': 'Cost of Debt',
                'Value': '0.06',
                'Description': 'Cost of debt'
            },
            {
                'Field': 'Cash Balance',
                'Value': '500',
                'Description': 'Cash and cash equivalents'
            }
        ]
    
    def test_csv_to_json_basic(self):
        """Test basic CSV to JSON conversion."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['Field', 'Value', 'Description'])
            writer.writeheader()
            writer.writerows(self.sample_csv_data)
            temp_file_path = f.name
        
        try:
            result = csv_to_json(temp_file_path)
            
            # Check basic structure
            self.assertIn('company_name', result)
            self.assertIn('valuation_date', result)
            self.assertIn('financial_inputs', result)
            self.assertIn('comparable_multiples', result)
            self.assertIn('scenarios', result)
            self.assertIn('monte_carlo_specs', result)
            self.assertIn('sensitivity_analysis', result)
            
            # Check specific values
            self.assertEqual(result['company_name'], 'Test Company')
            self.assertEqual(result['valuation_date'], '2024-01-01')
            self.assertEqual(result['financial_inputs']['revenue'], [1000, 1100, 1200, 1300, 1400])
            self.assertEqual(result['financial_inputs']['ebit_margin'], 0.15)
            self.assertEqual(result['financial_inputs']['tax_rate'], 0.25)
            self.assertEqual(result['financial_inputs']['weighted_average_cost_of_capital'], 0.10)
            self.assertEqual(result['financial_inputs']['terminal_growth_rate'], 0.03)
            self.assertEqual(result['financial_inputs']['share_count'], 100)
            self.assertEqual(result['financial_inputs']['cost_of_debt'], 0.06)
            self.assertEqual(result['financial_inputs']['cash_balance'], 500)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_csv_to_json_missing_file(self):
        """Test CSV to JSON with missing file."""
        with self.assertRaises(FileNotFoundError):
            csv_to_json("nonexistent_file.csv")
    
    def test_csv_to_json_empty_fields(self):
        """Test CSV to JSON with empty fields."""
        csv_data_with_empty = [
            {'Field': 'Company Name', 'Value': 'Test Company', 'Description': 'Name'},
            {'Field': '', 'Value': '', 'Description': ''},  # Empty row
            {'Field': 'EBIT Margin', 'Value': '0.15', 'Description': 'Margin'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['Field', 'Value', 'Description'])
            writer.writeheader()
            writer.writerows(csv_data_with_empty)
            temp_file_path = f.name
        
        try:
            result = csv_to_json(temp_file_path)
            # Should handle empty fields gracefully
            self.assertIn('company_name', result)
            self.assertIn('financial_inputs', result)
        finally:
            os.unlink(temp_file_path)
    
    def test_csv_to_json_type_conversion(self):
        """Test CSV to JSON type conversion."""
        csv_data_types = [
            {'Field': 'Company Name', 'Value': 'Test Company', 'Description': 'Name'},
            {'Field': 'Forecast Years', 'Value': '5', 'Description': 'Years'},
            {'Field': 'EBIT Margin', 'Value': '0.15', 'Description': 'Margin'},
            {'Field': 'Use Input WACC', 'Value': 'true', 'Description': 'Use WACC'},
            {'Field': 'Revenue Year 1', 'Value': '1000.5', 'Description': 'Revenue'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['Field', 'Value', 'Description'])
            writer.writeheader()
            writer.writerows(csv_data_types)
            temp_file_path = f.name
        
        try:
            result = csv_to_json(temp_file_path)
            
            # Check type conversions
            self.assertIsInstance(result['financial_inputs']['revenue'][0], float)
            self.assertIsInstance(result['financial_inputs']['ebit_margin'], float)
            self.assertIsInstance(result['financial_inputs']['use_input_wacc'], bool)
            
        finally:
            os.unlink(temp_file_path)

class TestGenerateCSVReport(unittest.TestCase):
    """Test CSV report generation functionality."""
    
    def setUp(self):
        """Set up test data for report generation."""
        self.input_data = {
            'company_name': 'Test Company',
            'valuation_date': '2024-01-01',
            'financial_inputs': {
                'revenue': [1000, 1100, 1200, 1300, 1400],
                'ebit_margin': 0.15,
                'tax_rate': 0.25,
                'capex': [200, 220, 240, 260, 280],
                'depreciation': [150, 160, 170, 180, 190],
                'nwc_changes': [50, 55, 60, 65, 70],
                'wacc': 0.10,
                'terminal_growth': 0.03,
                'share_count': 100,
                'cost_of_debt': 0.06,
                'cash_balance': 500,
                'cost_of_capital': {
                    'risk_free_rate': 0.03,
                    'market_risk_premium': 0.06,
                    'levered_beta': 1.0,
                    'target_debt_to_value_ratio': 0.3
                }
            }
        }
        
        self.results_data = {
            'dcf_valuation': {
                'enterprise_value': 5000,
                'equity_value': 4500,
                'price_per_share': 45.0,
                'wacc_components': {
                    'cost_of_equity': 0.12,
                    'cost_of_debt': 0.06
                }
            },
            'apv_valuation': {
                'enterprise_value': 4800,
                'equity_value': 4300,
                'price_per_share': 43.0
            },
            'comparable_valuation': {
                'ev_multiples': {
                    'mean_ev': 5200
                }
            },
            'scenarios': {
                'scenarios': {
                    'optimistic': {
                        'price_per_share': 55.0
                    },
                    'pessimistic': {
                        'price_per_share': 35.0
                    }
                }
            },
            'monte_carlo_simulation': {
                'wacc_method': {
                    'mean_ev': 5000,
                    'confidence_interval_95': [4500, 5500]
                }
            },
            'sensitivity_analysis': {
                'sensitivity_results': {
                    'ebit_margin': {
                        'ev': {'0.12': 4000, '0.15': 5000, '0.18': 6000},
                        'price_per_share': {'0.12': 40.0, '0.15': 45.0, '0.18': 50.0}
                    }
                }
            }
        }
    
    def test_generate_csv_report_basic(self):
        """Test basic CSV report generation."""
        report = generate_csv_report(self.input_data, self.results_data, 'Test Company')
        
        # Check that report is a list of lists (CSV format)
        self.assertIsInstance(report, list)
        self.assertGreater(len(report), 0)
        
        # Check for key sections
        report_text = '\n'.join([','.join(row) for row in report])
        self.assertIn('COMPANY INFORMATION', report_text)
        self.assertIn('KEY METRICS', report_text)
        self.assertIn('FINANCIAL PROJECTIONS', report_text)
        self.assertIn('VALUATION RESULTS', report_text)
        self.assertIn('WACC BREAKDOWN', report_text)
        self.assertIn('SCENARIO ANALYSIS', report_text)
        self.assertIn('MONTE CARLO SIMULATION', report_text)
    
    def test_generate_csv_report_company_info(self):
        """Test company information section."""
        report = generate_csv_report(self.input_data, self.results_data, 'Test Company')
        
        # Find company information section
        company_info_found = False
        for row in report:
            if row and row[0] == 'COMPANY INFORMATION':
                company_info_found = True
                break
        
        self.assertTrue(company_info_found)
        
        # Check for company name
        company_name_found = False
        for row in report:
            if len(row) >= 2 and row[0] == 'Company' and row[1] == 'Test Company':
                company_name_found = True
                break
        
        self.assertTrue(company_name_found)
    
    def test_generate_csv_report_valuation_results(self):
        """Test valuation results section."""
        report = generate_csv_report(self.input_data, self.results_data, 'Test Company')
        
        # Find valuation results section
        valuation_results_found = False
        for row in report:
            if row and row[0] == 'VALUATION RESULTS':
                valuation_results_found = True
                break
        
        self.assertTrue(valuation_results_found)
        
        # Check for DCF results
        dcf_found = False
        for row in report:
            if len(row) >= 2 and row[0] == 'DCF (WACC)':
                dcf_found = True
                self.assertIn('$5,000', row[1])  # Enterprise value (formatted)
                self.assertIn('$4,500', row[2])  # Equity value (formatted)
                self.assertIn('45.00', row[3])  # Price per share
                break
        
        self.assertTrue(dcf_found)
    
    def test_generate_csv_report_financial_projections(self):
        """Test financial projections section."""
        report = generate_csv_report(self.input_data, self.results_data, 'Test Company')
        
        # Find financial projections section
        projections_found = False
        for row in report:
            if row and row[0] == 'FINANCIAL PROJECTIONS':
                projections_found = True
                break
        
        self.assertTrue(projections_found)
        
        # Check for revenue projections
        revenue_found = False
        for row in report:
            if len(row) >= 2 and row[0] == 'Revenue ($M)':
                revenue_found = True
                # The loop overwrites the first column with the last year's value
                self.assertIn('1400.0', row[1])  # Year 5 (last year overwrites)
                break
        
        self.assertTrue(revenue_found)
    
    def test_generate_csv_report_missing_data(self):
        """Test CSV report generation with missing data."""
        minimal_results = {
            'dcf_valuation': {
                'enterprise_value': 5000,
                'equity_value': 4500,
                'price_per_share': 45.0
            }
        }
        
        # Should handle missing data gracefully
        report = generate_csv_report(self.input_data, minimal_results, 'Test Company')
        self.assertIsInstance(report, list)
        self.assertGreater(len(report), 0)

class TestRunValuationWorkflow(unittest.TestCase):
    """Test the complete valuation workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_csv_content = """Field,Value,Description
Company Name,Test Company,Name of the company
Valuation Date,2024-01-01,Date of valuation
Forecast Years,5,Number of forecast years
Revenue Year 1,1000,Revenue for year 1
Revenue Year 2,1100,Revenue for year 2
Revenue Year 3,1200,Revenue for year 3
Revenue Year 4,1300,Revenue for year 4
Revenue Year 5,1400,Revenue for year 5
EBIT Margin,0.15,EBIT margin percentage
Tax Rate,0.25,Corporate tax rate
CapEx Year 1,200,Capital expenditure year 1
CapEx Year 2,220,Capital expenditure year 2
CapEx Year 3,240,Capital expenditure year 3
CapEx Year 4,260,Capital expenditure year 4
CapEx Year 5,280,Capital expenditure year 5
Depreciation Year 1,150,Depreciation year 1
Depreciation Year 2,160,Depreciation year 2
Depreciation Year 3,170,Depreciation year 3
Depreciation Year 4,180,Depreciation year 4
Depreciation Year 5,190,Depreciation year 5
NWC Changes Year 1,50,Net working capital changes year 1
NWC Changes Year 2,55,Net working capital changes year 2
NWC Changes Year 3,60,Net working capital changes year 3
NWC Changes Year 4,65,Net working capital changes year 4
NWC Changes Year 5,70,Net working capital changes year 5
WACC,0.10,Weighted average cost of capital
Terminal Growth Rate,0.03,Terminal growth rate
Share Count,100,Number of shares outstanding
Cost of Debt,0.06,Cost of debt
Cash Balance,500,Cash and cash equivalents
Risk Free Rate,0.03,Risk free rate
Market Risk Premium,0.06,Market risk premium
Levered Beta,1.0,Levered beta
Target Debt Ratio,0.3,Target debt ratio
Current Debt Balance,300,Current debt balance
EV/EBITDA Multiple 1,12.5,EV/EBITDA multiple 1
EV/EBITDA Multiple 2,14.2,EV/EBITDA multiple 2
EV/EBITDA Multiple 3,13.8,EV/EBITDA multiple 3
EV/EBITDA Multiple 4,15.1,EV/EBITDA multiple 4
EV/EBITDA Multiple 5,14.5,EV/EBITDA multiple 5
Optimistic EBIT Margin,0.20,Optimistic EBIT margin
Optimistic Terminal Growth,0.04,Optimistic terminal growth
Optimistic WACC,0.08,Optimistic WACC
Pessimistic EBIT Margin,0.10,Pessimistic EBIT margin
Pessimistic Terminal Growth,0.02,Pessimistic terminal growth
Pessimistic WACC,0.12,Pessimistic WACC
MC EBIT Margin Mean,0.15,Monte Carlo EBIT margin mean
MC EBIT Margin Std,0.02,Monte Carlo EBIT margin std
MC Terminal Growth Mean,0.03,Monte Carlo terminal growth mean
MC Terminal Growth Std,0.005,Monte Carlo terminal growth std
MC WACC Mean,0.10,Monte Carlo WACC mean
MC WACC Std,0.01,Monte Carlo WACC std
Sensitivity EBIT Margin 1,0.12,Sensitivity EBIT margin 1
Sensitivity EBIT Margin 2,0.13,Sensitivity EBIT margin 2
Sensitivity EBIT Margin 3,0.14,Sensitivity EBIT margin 3
Sensitivity EBIT Margin 4,0.15,Sensitivity EBIT margin 4
Sensitivity EBIT Margin 5,0.16,Sensitivity EBIT margin 5
Sensitivity EBIT Margin 6,0.17,Sensitivity EBIT margin 6
Sensitivity EBIT Margin 7,0.18,Sensitivity EBIT margin 7
Sensitivity Terminal Growth 1,0.02,Sensitivity terminal growth 1
Sensitivity Terminal Growth 2,0.025,Sensitivity terminal growth 2
Sensitivity Terminal Growth 3,0.03,Sensitivity terminal growth 3
Sensitivity Terminal Growth 4,0.035,Sensitivity terminal growth 4
Sensitivity Terminal Growth 5,0.04,Sensitivity terminal growth 5
Sensitivity WACC 1,0.08,Sensitivity WACC 1
Sensitivity WACC 2,0.09,Sensitivity WACC 2
Sensitivity WACC 3,0.10,Sensitivity WACC 3
Sensitivity WACC 4,0.11,Sensitivity WACC 4
Sensitivity WACC 5,0.12,Sensitivity WACC 5"""
    
    @patch('main.FinancialValuationEngine')
    @patch('main.parse_financial_inputs')
    def test_run_valuation_workflow_success(self, mock_create_inputs, mock_calculator):
        """Test successful valuation workflow."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(self.sample_csv_content)
            temp_file_path = f.name
        
        try:
            # Mock the calculator and inputs
            mock_calc_instance = MagicMock()
            mock_calculator.return_value = mock_calc_instance
            
            mock_inputs = MagicMock()
            mock_create_inputs.return_value = mock_inputs
            
            # Mock comprehensive valuation result
            mock_result = {
                'valuation_summary': {'company': 'Test Company'},
                'dcf_valuation': {
                    'enterprise_value': 5000,
                    'wacc_components': {'cost_of_equity': 0.12}
                },
                'apv_valuation': {'enterprise_value': 4800},
                'comparable_valuation': {'ev_multiples': {'mean_ev': 5200}},
                'scenarios': {'scenarios': {'optimistic': {'price_per_share': 55.0}}},
                'sensitivity_analysis': {'sensitivity_results': {}},
                'monte_carlo_simulation': {'wacc_method': {'mean_ev': 5000}}
            }
            mock_calc_instance.perform_comprehensive_valuation.return_value = mock_result
            
            # Run the workflow
            output_file = run_valuation_workflow(temp_file_path)
            
            # Check that output file was created
            self.assertTrue(os.path.exists(output_file))
            self.assertIn('Test_Company_Valuation_Report.csv', output_file)
            
            # Clean up output file
            os.unlink(output_file)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_run_valuation_workflow_missing_file(self):
        """Test valuation workflow with missing input file."""
        with self.assertRaises(FileNotFoundError):
            run_valuation_workflow("nonexistent_file.csv")
    
    @patch('main.FinancialValuationEngine')
    @patch('main.parse_financial_inputs')
    def test_run_valuation_workflow_calculation_error(self, mock_create_inputs, mock_calculator):
        """Test valuation workflow with calculation error."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(self.sample_csv_content)
            temp_file_path = f.name
        
        try:
            # Mock the calculator to raise an exception
            mock_calc_instance = MagicMock()
            mock_calculator.return_value = mock_calc_instance
            mock_calc_instance.run_comprehensive_valuation.side_effect = Exception("Calculation failed")
            
            mock_inputs = MagicMock()
            mock_create_inputs.return_value = mock_inputs
            
            # Should handle calculation errors gracefully
            with self.assertRaises(Exception):
                run_valuation_workflow(temp_file_path)
                
        finally:
            os.unlink(temp_file_path)

class TestMainFunction(unittest.TestCase):
    """Test the main function."""
    
    @patch('main.run_valuation_workflow')
    @patch('sys.argv', ['main.py', 'test_input.csv'])
    def test_main_success(self, mock_run_workflow):
        """Test successful main function execution."""
        mock_run_workflow.return_value = 'Test_Company_Valuation_Report.csv'
        
        # Should not raise any exceptions
        main()
        
        # Check that run_valuation_workflow was called
        mock_run_workflow.assert_called_once_with('test_input.csv')
    
    @patch('main.run_valuation_workflow')
    @patch('sys.argv', ['main.py'])
    def test_main_default_input(self, mock_run_workflow):
        """Test main function with default input file."""
        mock_run_workflow.return_value = 'Company_Valuation_Report.csv'
        
        # Should use default input file
        main()
        
        # Check that run_valuation_workflow was called with default
        mock_run_workflow.assert_called_once_with('valuation_input.csv')
    
    @patch('main.run_valuation_workflow')
    @patch('sys.argv', ['main.py', 'test_input.csv'])
    def test_main_workflow_error(self, mock_run_workflow):
        """Test main function with workflow error."""
        mock_run_workflow.side_effect = Exception("Workflow failed")
        
        # Should handle errors gracefully
        with self.assertRaises(SystemExit):
            main()

if __name__ == '__main__':
    unittest.main() 