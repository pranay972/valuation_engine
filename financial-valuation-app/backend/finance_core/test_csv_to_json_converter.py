#!/usr/bin/env python3
"""
Unit Tests for CSV to JSON Converter

Tests the CSV to JSON conversion functionality in csv_to_json_converter.py
"""

import unittest
import json
import tempfile
import os
import sys
import csv
from unittest.mock import patch, mock_open

# Import the modules to test
from csv_to_json_converter import csv_to_json, convert_csv_to_json_file

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
                'Description': 'NWC changes year 1'
            },
            {
                'Field': 'NWC Changes Year 2',
                'Value': '55',
                'Description': 'NWC changes year 2'
            },
            {
                'Field': 'NWC Changes Year 3',
                'Value': '60',
                'Description': 'NWC changes year 3'
            },
            {
                'Field': 'NWC Changes Year 4',
                'Value': '65',
                'Description': 'NWC changes year 4'
            },
            {
                'Field': 'NWC Changes Year 5',
                'Value': '70',
                'Description': 'NWC changes year 5'
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
                'Description': 'Cash balance'
            },
            {
                'Field': 'Risk Free Rate',
                'Value': '0.03',
                'Description': 'Risk-free rate'
            },
            {
                'Field': 'Market Risk Premium',
                'Value': '0.06',
                'Description': 'Market risk premium'
            },
            {
                'Field': 'Levered Beta',
                'Value': '1.2',
                'Description': 'Levered beta'
            },
            {
                'Field': 'Target Debt Ratio',
                'Value': '0.3',
                'Description': 'Target debt ratio'
            },
            {
                'Field': 'Current Debt Balance',
                'Value': '300',
                'Description': 'Current debt balance'
            },
            {
                'Field': 'Use Input WACC',
                'Value': 'True',
                'Description': 'Use input WACC'
            },
            {
                'Field': 'Use Debt Schedule',
                'Value': 'False',
                'Description': 'Use debt schedule'
            }
        ]
    
    def test_csv_to_json_basic(self):
        """Test basic CSV to JSON conversion."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            writer = csv.DictWriter(temp_file, fieldnames=['Field', 'Value', 'Description'])
            writer.writeheader()
            writer.writerows(self.sample_csv_data)
            temp_file_path = temp_file.name
        
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
            
        finally:
            os.unlink(temp_file_path)
    
    def test_csv_to_json_missing_file(self):
        """Test CSV to JSON conversion with missing file."""
        with self.assertRaises(FileNotFoundError):
            csv_to_json("nonexistent_file.csv")
    
    def test_csv_to_json_empty_fields(self):
        """Test CSV to JSON conversion with empty fields."""
        # Create temporary CSV file with empty fields
        csv_data_with_empty = [
            {'Field': 'Company Name', 'Value': 'Test Company', 'Description': 'Name'},
            {'Field': '', 'Value': '1000', 'Description': 'Empty field'},
            {'Field': 'Revenue Year 1', 'Value': '', 'Description': 'Empty value'},
            {'Field': 'Revenue Year 2', 'Value': '1100', 'Description': 'Valid field'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            writer = csv.DictWriter(temp_file, fieldnames=['Field', 'Value', 'Description'])
            writer.writeheader()
            writer.writerows(csv_data_with_empty)
            temp_file_path = temp_file.name
        
        try:
            result = csv_to_json(temp_file_path)
            
            # Should only include valid fields
            self.assertEqual(result['company_name'], 'Test Company')
            self.assertEqual(result['financial_inputs']['revenue'][1], 1100)  # Year 2 should be included
            self.assertEqual(result['financial_inputs']['revenue'][0], 0)  # Year 1 should be default
            
        finally:
            os.unlink(temp_file_path)
    
    def test_csv_to_json_type_conversion(self):
        """Test CSV to JSON conversion with type conversion."""
        # Create temporary CSV file with various data types
        csv_data_types = [
            {'Field': 'Company Name', 'Value': 'Test Company', 'Description': 'String'},
            {'Field': 'Forecast Years', 'Value': '5', 'Description': 'Integer'},
            {'Field': 'EBIT Margin', 'Value': '0.15', 'Description': 'Float'},
            {'Field': 'Use Input WACC', 'Value': 'True', 'Description': 'Boolean'},
            {'Field': 'Share Count', 'Value': '100.5', 'Description': 'Float'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            writer = csv.DictWriter(temp_file, fieldnames=['Field', 'Value', 'Description'])
            writer.writeheader()
            writer.writerows(csv_data_types)
            temp_file_path = temp_file.name
        
        try:
            result = csv_to_json(temp_file_path)
            
            # Check type conversions
            self.assertEqual(result['company_name'], 'Test Company')  # String
            self.assertEqual(result['forecast_years'], 5)  # Integer
            self.assertEqual(result['financial_inputs']['ebit_margin'], 0.15)  # Float
            self.assertEqual(result['financial_inputs']['use_input_wacc'], True)  # Boolean
            self.assertEqual(result['financial_inputs']['share_count'], 100.5)  # Float
            
        finally:
            os.unlink(temp_file_path)

class TestConvertCSVToJSONFile(unittest.TestCase):
    """Test CSV to JSON file conversion functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_csv_data = [
            {'Field': 'Company Name', 'Value': 'Test Company', 'Description': 'Name'},
            {'Field': 'Revenue Year 1', 'Value': '1000', 'Description': 'Revenue'},
            {'Field': 'EBIT Margin', 'Value': '0.15', 'Description': 'Margin'}
        ]
    
    def test_convert_csv_to_json_file_basic(self):
        """Test basic CSV to JSON file conversion."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_csv:
            writer = csv.DictWriter(temp_csv, fieldnames=['Field', 'Value', 'Description'])
            writer.writeheader()
            writer.writerows(self.sample_csv_data)
            temp_csv_path = temp_csv.name
        
        # Create temporary JSON file path
        temp_json_path = temp_csv_path.replace('.csv', '.json')
        
        try:
            # Convert CSV to JSON file
            output_path = convert_csv_to_json_file(temp_csv_path, temp_json_path)
            
            # Check that file was created
            self.assertTrue(os.path.exists(output_path))
            self.assertEqual(output_path, temp_json_path)
            
            # Check file contents
            with open(output_path, 'r') as f:
                result = json.load(f)
            
            self.assertEqual(result['company_name'], 'Test Company')
            self.assertEqual(result['financial_inputs']['revenue'][0], 1000)
            self.assertEqual(result['financial_inputs']['ebit_margin'], 0.15)
            
        finally:
            # Clean up
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
            if os.path.exists(temp_json_path):
                os.unlink(temp_json_path)
    
    def test_convert_csv_to_json_file_auto_filename(self):
        """Test CSV to JSON file conversion with auto-generated filename."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_csv:
            writer = csv.DictWriter(temp_csv, fieldnames=['Field', 'Value', 'Description'])
            writer.writeheader()
            writer.writerows(self.sample_csv_data)
            temp_csv_path = temp_csv.name
        
        try:
            # Convert CSV to JSON file without specifying output path
            output_path = convert_csv_to_json_file(temp_csv_path)
            
            # Check that file was created with expected name
            expected_name = os.path.splitext(os.path.basename(temp_csv_path))[0] + '.json'
            self.assertEqual(os.path.basename(output_path), expected_name)
            self.assertTrue(os.path.exists(output_path))
            
            # Check file contents
            with open(output_path, 'r') as f:
                result = json.load(f)
            
            self.assertEqual(result['company_name'], 'Test Company')
            
        finally:
            # Clean up
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_convert_csv_to_json_file_missing_input(self):
        """Test CSV to JSON file conversion with missing input file."""
        with self.assertRaises(FileNotFoundError):
            convert_csv_to_json_file("nonexistent_file.csv")
    
    def test_convert_csv_to_json_file_invalid_csv(self):
        """Test CSV to JSON file conversion with invalid CSV."""
        # Create temporary file with invalid CSV content (missing required headers)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_csv:
            temp_csv.write("Invalid,CSV,Content\n")
            temp_csv.write("No,Required,Headers\n")
            temp_csv_path = temp_csv.name
        
        try:
            # This should not raise an error but should handle gracefully
            output_path = convert_csv_to_json_file(temp_csv_path)
            
            # Check that file was created with default values
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r') as f:
                result = json.load(f)
            
            # Should have default values
            self.assertEqual(result['company_name'], 'Unknown Company')
            
        finally:
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

if __name__ == '__main__':
    unittest.main() 