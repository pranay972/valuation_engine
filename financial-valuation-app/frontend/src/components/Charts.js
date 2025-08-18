import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis, YAxis
} from 'recharts';

export function DCFChart({ data }) {
  const chartData = data?.free_cash_flows_after_tax_fcff?.map((fcf, index) => ({
    year: `Year ${index + 1}`,
    fcf: fcf
  })) || [];
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="year" />
        <YAxis />
        <Tooltip formatter={(value) => [`$${value}M`, 'Free Cash Flow']} />
        <Legend />
        <Line type="monotone" dataKey="fcf" stroke="#8884d8" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function SensitivityChart({ data }) {
  const chartData = Object.entries(data || {}).map(([param, values]) => ({
    parameter: param,
    min: Math.min(...Object.values(values.ev)),
    max: Math.max(...Object.values(values.ev)),
    current: values.ev['0.095'] || values.ev['0.18'] || values.ev['0.025']
  }));
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="parameter" />
        <YAxis />
        <Tooltip formatter={(value) => [`$${value}M`, 'Enterprise Value']} />
        <Legend />
        <Bar dataKey="min" fill="#ff6b6b" name="Min" />
        <Bar dataKey="current" fill="#4ecdc4" name="Current" />
        <Bar dataKey="max" fill="#45b7d1" name="Max" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function MonteCarloChart({ data }) {
  // Simulate Monte Carlo distribution
  const distribution = Array.from({ length: 100 }, (_, i) => ({
    value: data?.wacc_method?.mean_ev + (Math.random() - 0.5) * (data?.wacc_method?.std_dev || 1) * 2,
    frequency: Math.random() * 10
  }));
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={distribution}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="value" />
        <YAxis />
        <Tooltip formatter={(value) => [value, 'Frequency']} />
        <Bar dataKey="frequency" fill="#9c88ff" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ScenarioChart({ data }) {
  const chartData = Object.entries(data || {}).map(([scenario, values]) => ({
    scenario: scenario.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    enterpriseValue: values.ev || 0,
    equityValue: values.equity || 0,
    pricePerShare: values.price_per_share || 0
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="scenario" />
        <YAxis />
        <Tooltip formatter={(value) => [`$${value}M`, 'Value']} />
        <Legend />
        <Bar dataKey="enterpriseValue" fill="#007bff" name="Enterprise Value" />
        <Bar dataKey="equityValue" fill="#28a745" name="Equity Value" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ComparableMultiplesChart({ data }) {
  if (!data || !data.implied_evs_by_multiple) return null;

  const chartData = Object.entries(data.implied_evs_by_multiple).map(([multiple, values]) => ({
    multiple: multiple,
    meanImpliedEV: values.mean_implied_ev || 0,
    medianImpliedEV: values.median_implied_ev || 0,
    meanMultiple: values.mean_multiple || 0
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="multiple" />
        <YAxis />
        <Tooltip formatter={(value) => [`$${value}M`, 'Enterprise Value']} />
        <Legend />
        <Bar dataKey="meanImpliedEV" fill="#007bff" name="Mean Implied EV" />
        <Bar dataKey="medianImpliedEV" fill="#28a745" name="Median Implied EV" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function APVChart({ data }) {
  if (!data || !data.unlevered_fcfs_used) return null;

  const chartData = data.unlevered_fcfs_used.map((fcf, index) => ({
    year: `Year ${index + 1}`,
    unleveredFCF: fcf
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="year" />
        <YAxis />
        <Tooltip formatter={(value) => [`$${value}M`, 'Unlevered FCF']} />
        <Legend />
        <Line type="monotone" dataKey="unleveredFCF" stroke="#28a745" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
} 