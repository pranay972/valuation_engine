import json
import os
from math import isclose
from pathlib import Path

import pytest

from app import create_app, db
from app.models import Analysis, AnalysisInput, AnalysisResult


def _load_input_json():
    """Load input JSON for the test.

    Uses TEST_INPUT_JSON env var if set, otherwise defaults to finance_core/sample_input.json
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    default_path = os.path.join(base_dir, 'finance_core', 'sample_input.json')
    input_path = os.environ.get('TEST_INPUT_JSON', default_path)
    with open(input_path, 'r') as f:
        return json.load(f), input_path


def _load_validation_json():
    """Load output validation JSON for comparison."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    validation_path = os.path.join(base_dir, 'finance_core', 'output_validation.json')
    with open(validation_path, 'r') as f:
        return json.load(f), validation_path


def _compare_values(actual, expected, tolerance=0.05, path=""):
    diffs = []
    if isinstance(actual, dict) and isinstance(expected, dict):
        common = actual.keys() & expected.keys()
        for key in common:
            diffs.extend(_compare_values(actual[key], expected[key], tolerance, f"{path}.{key}" if path else key))
        return diffs
    if isinstance(actual, list) and isinstance(expected, list):
        for i, (a, e) in enumerate(zip(actual, expected)):
            diffs.extend(_compare_values(a, e, tolerance, f"{path}[{i}]" if path else f"[{i}]"))
        return diffs
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        if not isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
            diffs.append(f"{path}: {actual} vs {expected}")
        return diffs
    if actual != expected:
        diffs.append(f"{path}: {actual} vs {expected}")
    return diffs


def _assert_close(a, b, tol=0.01, msg=""):
    if a is None and b is None:
        return
    assert isclose(float(a), float(b), rel_tol=tol, abs_tol=tol), msg or f"{a} != {b} (tol {tol})"


def _require_keys(d: dict, keys: list[str], ctx: str):
    missing = [k for k in keys if k not in d]
    assert not missing, f"Missing keys in {ctx}: {missing}"


def test_api_matches_local_full_output():
    app = create_app('testing')
    client = app.test_client()

    sample, input_path = _load_input_json()
    validation, validation_path = _load_validation_json()
    artifacts_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), 'artifacts')))
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    print(f"Running full output comparison test...")

    with app.app_context():
        db.drop_all()
        db.create_all()

        # Compute local full comprehensive JSON
        from finance_core.finance_calculator import FinancialValuationEngine, parse_financial_inputs
        engine = FinancialValuationEngine()
        local_inputs = parse_financial_inputs(sample)
        local_full = engine.perform_comprehensive_valuation(
            inputs=local_inputs,
            company_name=sample.get('company_name', 'Company'),
            valuation_date=sample.get('valuation_date', '2024-01-01'),
        )

        # Save local full JSON
        input_name = Path(input_path).stem
        with (artifacts_dir / f"local_full_{input_name}.json").open('w') as f:
            json.dump(local_full, f, indent=2)

        # For API, we run each analysis type and combine normalized sections
        type_to_key = {
            'dcf_wacc': 'dcf_valuation',
            'apv': 'apv_valuation',
            'multiples': 'comparable_valuation',
            'scenario': 'scenarios',
            'sensitivity': 'sensitivity_analysis',
            'monte_carlo': 'monte_carlo_simulation',
        }

        combined_api: dict = {}
        for analysis_type, section_key in type_to_key.items():
            # Create analysis row
            analysis = Analysis(
                name=f"{analysis_type} parity test",
                analysis_type=analysis_type,
                company_name=sample.get('company_name', 'Company'),
                status='pending',
            )
            db.session.add(analysis)
            db.session.commit()

            # Persist inputs
            analysis_input = AnalysisInput(
                analysis_id=analysis.id,
                financial_inputs=sample.get('financial_inputs', {}),
                comparable_multiples=sample.get('comparable_multiples'),
                scenarios=sample.get('scenarios'),
                sensitivity_analysis=sample.get('sensitivity_analysis'),
                monte_carlo_specs=sample.get('monte_carlo_specs'),
            )
            db.session.add(analysis_input)
            db.session.commit()

            # Run via service (same as worker)
            from app.services.finance_core_service import FinanceCoreService
            service = FinanceCoreService()
            inputs_payload = {
                'financial_inputs': analysis_input.financial_inputs,
                'comparable_multiples': analysis_input.comparable_multiples,
                'scenarios': analysis_input.scenarios,
                'sensitivity_analysis': analysis_input.sensitivity_analysis,
                'monte_carlo_specs': analysis_input.monte_carlo_specs,
            }
            api_run = service.run_analysis(analysis_type, inputs_payload, analysis.company_name)
            assert api_run.get('success'), f"API run failed: {api_run}"

            # Save and mark completed like worker
            db.session.add(AnalysisResult(analysis_id=analysis.id, results_data=api_run['results']))
            analysis.status = 'completed'
            db.session.commit()

            # Fetch via API (normalized)
            resp = client.get(f"/api/results/{analysis.id}/results")
            assert resp.status_code == 200
            api_results_data = resp.get_json()['data']['results']['results_data']
            assert section_key in api_results_data, f"API missing section {section_key}"
            combined_api[section_key] = api_results_data[section_key]

        # Save API full JSON
        with (artifacts_dir / f"api_full_{input_name}.json").open('w') as f:
            json.dump(combined_api, f, indent=2)

        # Compare all top-level sections present in local_full
        common_keys = combined_api.keys() & local_full.keys()
        diffs = _compare_values({k: combined_api[k] for k in common_keys}, {k: local_full[k] for k in common_keys}, tolerance=0.01)
        if diffs:
            print(f"Found {len(diffs)} differences in full output:")
            for d in diffs[:50]:
                print(f"   - {d}")
        else:
            print("✅ All sections match exactly!")
        assert not diffs, "Differences found in full output:\n" + "\n".join(diffs[:50])

        # Three-way comparison with validation file
        print(f"\nThree-way comparison: Local vs API vs Validation...")
        validation_sections = validation.keys() & common_keys
        
        # Compare local vs validation
        local_vs_validation = _compare_values({k: local_full[k] for k in validation_sections}, {k: validation[k] for k in validation_sections}, tolerance=0.01)
        if local_vs_validation:
            print(f"Local vs Validation differences ({len(local_vs_validation)}):")
            for d in local_vs_validation[:20]:
                print(f"   - {d}")
        else:
            print("✅ Local results match validation exactly!")
            
        # Compare API vs validation
        api_vs_validation = _compare_values({k: combined_api[k] for k in validation_sections}, {k: validation[k] for k in validation_sections}, tolerance=0.01)
        if api_vs_validation:
            print(f"API vs Validation differences ({len(api_vs_validation)}):")
            for d in api_vs_validation[:20]:
                print(f"   - {d}")
        else:
            print("✅ API results match validation exactly!")

        # Targeted assertions for DCF
        if 'dcf_valuation' in common_keys:
            print(f"\nDCF Validation:")
            api_dcf = combined_api['dcf_valuation']
            loc_dcf = local_full['dcf_valuation']
            _require_keys(api_dcf, ['enterprise_value', 'equity_value', 'price_per_share', 'net_debt_breakdown', 'wacc_components'], 'API DCF')
            _require_keys(loc_dcf, ['enterprise_value', 'equity_value', 'price_per_share', 'net_debt_breakdown', 'wacc_components'], 'Local DCF')
            
            print(f"  Enterprise Value: API={api_dcf['enterprise_value']}, Local={loc_dcf['enterprise_value']}")
            _assert_close(api_dcf['enterprise_value'], loc_dcf['enterprise_value'], 0.01, 'DCF EV mismatch')
            
            print(f"  Equity Value: API={api_dcf['equity_value']}, Local={loc_dcf['equity_value']}")
            _assert_close(api_dcf['equity_value'], loc_dcf['equity_value'], 0.01, 'DCF Equity mismatch')
            
            print(f"  Price Per Share: API={api_dcf['price_per_share']}, Local={loc_dcf['price_per_share']}")
            _assert_close(api_dcf['price_per_share'], loc_dcf['price_per_share'], 0.01, 'DCF PPS mismatch')
            
            print(f"  Current Debt: API={api_dcf['net_debt_breakdown']['current_debt']}, Local={loc_dcf['net_debt_breakdown']['current_debt']}")
            _assert_close(api_dcf['net_debt_breakdown']['current_debt'], loc_dcf['net_debt_breakdown']['current_debt'], 0.01, 'DCF current_debt mismatch')
            
            print(f"  Cost of Equity: API={api_dcf['wacc_components']['cost_of_equity']}, Local={loc_dcf['wacc_components']['cost_of_equity']}")
            _assert_close(api_dcf['wacc_components']['cost_of_equity'], loc_dcf['wacc_components']['cost_of_equity'], 0.01, 'DCF CoE mismatch')
            
            # Compare with validation if available
            if 'dcf_valuation' in validation:
                val_dcf = validation['dcf_valuation']
                print(f"  Validation: EV={val_dcf.get('enterprise_value', 'N/A')}, Equity={val_dcf.get('equity_value', 'N/A')}, PPS={val_dcf.get('price_per_share', 'N/A')}")
            print("  ✅ DCF validation passed")

        # Targeted assertions for APV
        if 'apv_valuation' in common_keys:
            print(f"\nAPV Validation:")
            api_apv = combined_api['apv_valuation']
            loc_apv = local_full['apv_valuation']
            _require_keys(api_apv, ['enterprise_value', 'equity_value', 'apv_components'], 'API APV')
            _require_keys(loc_apv, ['enterprise_value', 'equity_value', 'apv_components'], 'Local APV')
            
            print(f"  PV Tax Shield: API={api_apv['apv_components']['pv_tax_shield']}, Local={loc_apv['apv_components']['pv_tax_shield']}")
            _assert_close(api_apv['apv_components']['pv_tax_shield'], loc_apv['apv_components']['pv_tax_shield'], 0.01, 'APV PV tax shield mismatch')
            
            # Compare with validation if available
            if 'apv_valuation' in validation:
                val_apv = validation['apv_valuation']
                print(f"  Validation: PV Tax Shield={val_apv.get('apv_components', {}).get('pv_tax_shield', 'N/A')}, EV={val_apv.get('enterprise_value', 'N/A')}")
            print("  ✅ APV validation passed")

        # Targeted assertions for Sensitivity
        if 'sensitivity_analysis' in common_keys:
            print(f"\nSensitivity Validation:")
            api_sens = combined_api['sensitivity_analysis']
            loc_sens = local_full['sensitivity_analysis']
            if 'sensitivity_results' in api_sens and 'sensitivity_results' in loc_sens:
                api_wacc = api_sens['sensitivity_results'].get('weighted_average_cost_of_capital', {})
                loc_wacc = loc_sens['sensitivity_results'].get('weighted_average_cost_of_capital', {})
                for p in ['0.085', '0.095', '0.105']:
                    if 'ev' in api_wacc and 'ev' in loc_wacc and p in api_wacc['ev'] and p in loc_wacc['ev']:
                        print(f"  WACC {p} EV: API={api_wacc['ev'][p]}, Local={loc_wacc['ev'][p]}")
                        _assert_close(api_wacc['ev'][p], loc_wacc['ev'][p], 0.05, f'Sensitivity WACC EV {p} mismatch')
                print("  ✅ Sensitivity validation passed")

        print(f"\nFull output comparison test completed successfully!")


@pytest.mark.parametrize(
    "analysis_type,section_key",
    [
        ("dcf_wacc", "dcf_valuation"),
        ("apv", "apv_valuation"),
        ("multiples", "comparable_valuation"),
        ("scenario", "scenarios"),
        ("sensitivity", "sensitivity_analysis"),
        ("monte_carlo", "monte_carlo_simulation"),
    ],
)
def test_api_matches_local_verbose_by_analysis(analysis_type, section_key):
    """Verbose per-analysis test that logs any field mismatches with full paths."""
    app = create_app('testing')
    client = app.test_client()

    sample, input_path = _load_input_json()
    validation, validation_path = _load_validation_json()
    artifacts_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), 'artifacts')))
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    input_name = Path(input_path).stem
    
    print(f"Testing {analysis_type} -> {section_key} parity...")

    with app.app_context():
        db.drop_all()
        db.create_all()

        # Local compute for this analysis (use full then extract section)
        from finance_core.finance_calculator import FinancialValuationEngine, parse_financial_inputs
        engine = FinancialValuationEngine()
        local_inputs = parse_financial_inputs(sample)
        local_full = engine.perform_comprehensive_valuation(
            inputs=local_inputs,
            company_name=sample.get('company_name', 'Company'),
            valuation_date=sample.get('valuation_date', '2024-01-01'),
        )
        assert section_key in local_full, f"Local missing section {section_key}"
        local_section = local_full[section_key]

        # Create analysis row and persist inputs
        analysis = Analysis(
            name=f"{analysis_type} verbose parity",
            analysis_type=analysis_type,
            company_name=sample.get('company_name', 'Company'),
            status='pending',
        )
        db.session.add(analysis)
        db.session.commit()

        analysis_input = AnalysisInput(
            analysis_id=analysis.id,
            financial_inputs=sample.get('financial_inputs', {}),
            comparable_multiples=sample.get('comparable_multiples'),
            scenarios=sample.get('scenarios'),
            sensitivity_analysis=sample.get('sensitivity_analysis'),
            monte_carlo_specs=sample.get('monte_carlo_specs'),
        )
        db.session.add(analysis_input)
        db.session.commit()

        # Run via service and save like worker
        from app.services.finance_core_service import FinanceCoreService
        service = FinanceCoreService()
        inputs_payload = {
            'financial_inputs': analysis_input.financial_inputs,
            'comparable_multiples': analysis_input.comparable_multiples,
            'scenarios': analysis_input.scenarios,
            'sensitivity_analysis': analysis_input.sensitivity_analysis,
            'monte_carlo_specs': analysis_input.monte_carlo_specs,
        }
        api_run = service.run_analysis(analysis_type, inputs_payload, analysis.company_name)
        assert api_run.get('success'), f"API run failed: {api_run}"

        db.session.add(AnalysisResult(analysis_id=analysis.id, results_data=api_run['results']))
        analysis.status = 'completed'
        db.session.commit()

        # Fetch normalized via API
        resp = client.get(f"/api/results/{analysis.id}/results")
        assert resp.status_code == 200
        api_results_data = resp.get_json()['data']['results']['results_data']
        assert section_key in api_results_data, f"API missing section {section_key}"
        api_section = api_results_data[section_key]

        # Save per-analysis artifacts
        with (artifacts_dir / f"api_{input_name}_{analysis_type}.json").open('w') as f:
            json.dump(api_section, f, indent=2)
        with (artifacts_dir / f"local_{input_name}_{analysis_type}.json").open('w') as f:
            json.dump(local_section, f, indent=2)

        # Compare and log detailed diffs
        diffs = _compare_values(api_section, local_section, tolerance=0.01)
        if diffs:
            print(f"Found {len(diffs)} differences in {section_key} ({analysis_type}):")
            for d in diffs:
                print(f"   - {d}")
        else:
            print(f"✅ {analysis_type} ({section_key}) matches exactly!")
            
            # Show some key values for successful cases
            if section_key == 'dcf_valuation' and 'enterprise_value' in api_section:
                print(f"  Enterprise Value: {api_section['enterprise_value']}")
                print(f"  Equity Value: {api_section['equity_value']}")
                print(f"  Price Per Share: {api_section['price_per_share']}")
            elif section_key == 'apv_valuation' and 'apv_components' in api_section:
                print(f"  PV Tax Shield: {api_section['apv_components']['pv_tax_shield']}")
                print(f"  Enterprise Value: {api_section['enterprise_value']}")
            elif section_key == 'comparable_valuation' and 'enterprise_value' in api_section:
                print(f"  Enterprise Value: {api_section['enterprise_value']}")
                print(f"  Price Per Share: {api_section['price_per_share']}")
                
        assert not diffs, f"Differences found in {section_key} ({analysis_type}). See printed report."
        
        # Three-way comparison with validation
        print(f"\nThree-way comparison for {analysis_type}:")
        if section_key in validation:
            val_section = validation[section_key]
            
            # Compare local vs validation
            local_vs_val = _compare_values(local_section, val_section, tolerance=0.01)
            if local_vs_val:
                print(f"Local vs Validation differences ({len(local_vs_val)}):")
                for d in local_vs_val[:10]:
                    print(f"   - {d}")
            else:
                print("✅ Local results match validation exactly!")
                
            # Compare API vs validation
            api_vs_val = _compare_values(api_section, val_section, tolerance=0.01)
            if api_vs_val:
                print(f"API vs Validation differences ({len(api_vs_val)}):")
                for d in api_vs_val[:10]:
                    print(f"   - {d}")
            else:
                print("✅ API results match validation exactly!")
                
            # Show validation values for key metrics
            if section_key == 'dcf_valuation':
                print(f"  Validation: EV={val_section.get('enterprise_value', 'N/A')}, Equity={val_section.get('equity_value', 'N/A')}, PPS={val_section.get('price_per_share', 'N/A')}")
            elif section_key == 'apv_valuation':
                print(f"  Validation: PV Tax Shield={val_section.get('apv_components', {}).get('pv_tax_shield', 'N/A')}, EV={val_section.get('enterprise_value', 'N/A')}")
            elif section_key == 'comparable_valuation':
                print(f"  Validation: EV={val_section.get('enterprise_value', 'N/A')}")
        else:
            print(f"No validation section found for {section_key}")
        
        print(f"{analysis_type} test completed successfully!")


