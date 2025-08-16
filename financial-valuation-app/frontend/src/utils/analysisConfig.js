// Analysis-specific field configurations
export const ANALYSIS_FIELD_CONFIG = {
  dcf_wacc: {
    required: ['revenue', 'ebit_margin', 'weighted_average_cost_of_capital', 'terminal_growth_rate', 'share_count'],
    optional: ['capex', 'depreciation', 'nwc_changes', 'tax_rate', 'cost_of_debt', 'cash_balance'],
    sections: ['company_info', 'core_financials', 'cost_of_capital', 'projections']
  },
  apv: {
    required: ['revenue', 'ebit_margin', 'unlevered_cost_of_equity', 'terminal_growth_rate', 'share_count'],
    optional: ['debt_schedule', 'tax_rate', 'cost_of_debt', 'cash_balance'],
    sections: ['company_info', 'core_financials', 'cost_of_capital', 'debt_structure']
  },
  multiples: {
    required: ['ev_ebitda', 'pe_ratio', 'ev_fcf', 'ev_revenue'],
    optional: ['revenue', 'ebit_margin', 'share_count'],
    sections: ['company_info', 'comparable_analysis']
  },
  scenario: {
    required: ['revenue', 'ebit_margin', 'weighted_average_cost_of_capital', 'terminal_growth_rate'],
    optional: ['capex', 'depreciation', 'nwc_changes', 'tax_rate', 'share_count'],
    sections: ['company_info', 'scenario_definitions', 'base_case_inputs']
  },
  sensitivity: {
    required: ['revenue', 'ebit_margin', 'weighted_average_cost_of_capital', 'terminal_growth_rate'],
    optional: ['capex', 'depreciation', 'nwc_changes', 'tax_rate', 'share_count'],
    sections: ['company_info', 'sensitivity_ranges', 'base_case_inputs']
  },
  monte_carlo: {
    required: ['mc_runs', 'mc_ebit_margin_mean', 'mc_ebit_margin_std', 'mc_wacc_mean', 'mc_wacc_std'],
    optional: ['revenue', 'ebit_margin', 'weighted_average_cost_of_capital', 'terminal_growth_rate', 'share_count'],
    sections: ['company_info', 'monte_carlo_specs', 'base_case_inputs']
  }
};

// Get required sections for selected analyses
export const getRequiredSections = (selectedAnalyses) => {
  const requiredSections = new Set();
  
  selectedAnalyses.forEach(analysis => {
    const config = ANALYSIS_FIELD_CONFIG[analysis.id];
    if (config) {
      config.sections.forEach(section => requiredSections.add(section));
    }
  });
  
  return Array.from(requiredSections);
};

// Get required fields for selected analyses
export const getRequiredFields = (selectedAnalyses) => {
  const requiredFields = new Set();
  
  selectedAnalyses.forEach(analysis => {
    const config = ANALYSIS_FIELD_CONFIG[analysis.id];
    if (config) {
      config.required.forEach(field => requiredFields.add(field));
      config.optional.forEach(field => requiredFields.add(field));
    }
  });
  
  return Array.from(requiredFields);
};

// Check if a field should be shown for selected analyses
export const shouldShowField = (fieldName, selectedAnalyses) => {
  return selectedAnalyses.some(analysis => {
    const config = ANALYSIS_FIELD_CONFIG[analysis.id];
    if (!config) return false;
    return config.required.includes(fieldName) || config.optional.includes(fieldName);
  });
};

// Check if a section should be shown for selected analyses
export const shouldShowSection = (sectionName, selectedAnalyses) => {
  return selectedAnalyses.some(analysis => {
    const config = ANALYSIS_FIELD_CONFIG[analysis.id];
    if (!config) return false;
    return config.sections.includes(sectionName);
  });
};
