import React from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
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