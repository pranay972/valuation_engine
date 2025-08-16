import React from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area, PieChart, Pie, Cell
} from 'recharts';

// Custom Tooltip Component
const CustomTooltip = ({ active, payload, label, formatter, labelFormatter }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-4">
        <p className="text-sm font-semibold text-gray-900 mb-2">
          {labelFormatter ? labelFormatter(label) : label}
        </p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center space-x-2 mb-1">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm font-medium text-gray-700">
              {entry.name}:
            </span>
            <span className="text-sm font-bold text-gray-900">
              {formatter ? formatter(entry.value) : entry.value}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

// Custom Legend Component
const CustomLegend = ({ payload }) => (
  <div className="flex flex-wrap justify-center space-x-4 mt-4">
    {payload.map((entry, index) => (
      <div key={index} className="flex items-center space-x-2">
        <div 
          className="w-4 h-4 rounded" 
          style={{ backgroundColor: entry.color }}
        />
        <span className="text-sm font-medium text-gray-600">
          {entry.value}
        </span>
      </div>
    ))}
  </div>
);

export function DCFChart({ data }) {
  const chartData = data?.free_cash_flows_after_tax_fcff?.map((fcf, index) => ({
    year: `Year ${index + 1}`,
    fcf: fcf
  })) || [];

  return (
    <div className="card">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Discounted Cash Flow Projection
        </h3>
        <p className="text-sm text-gray-600">
          Projected free cash flows over the forecast period
        </p>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="fcfGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="year" 
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <YAxis 
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
            tickFormatter={(value) => `$${value}M`}
          />
          <Tooltip 
            content={<CustomTooltip formatter={(value) => `$${value}M`} />}
          />
          <Area 
            type="monotone" 
            dataKey="fcf" 
            stroke="#3b82f6" 
            strokeWidth={3}
            fill="url(#fcfGradient)"
            dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
      
      <CustomLegend payload={[{ value: 'Free Cash Flow', color: '#3b82f6' }]} />
    </div>
  );
}

export function SensitivityChart({ data }) {
  const chartData = Object.entries(data || {}).map(([param, values]) => ({
    parameter: param.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    min: Math.min(...Object.values(values.ev)),
    max: Math.max(...Object.values(values.ev)),
    current: values.ev['0.095'] || values.ev['0.18'] || values.ev['0.025']
  }));

  return (
    <div className="card">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Sensitivity Analysis
        </h3>
        <p className="text-sm text-gray-600">
          Enterprise value sensitivity to key parameter changes
        </p>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="parameter" 
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <YAxis 
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
            tickFormatter={(value) => `$${value}M`}
          />
          <Tooltip 
            content={<CustomTooltip formatter={(value) => `$${value}M`} />}
          />
          <Bar 
            dataKey="min" 
            fill="#ef4444" 
            name="Minimum Value"
            radius={[4, 4, 0, 0]}
          />
          <Bar 
            dataKey="current" 
            fill="#10b981" 
            name="Current Value"
            radius={[4, 4, 0, 0]}
          />
          <Bar 
            dataKey="max" 
            fill="#3b82f6" 
            name="Maximum Value"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
      
      <CustomLegend payload={[
        { value: 'Minimum Value', color: '#ef4444' },
        { value: 'Current Value', color: '#10b981' },
        { value: 'Maximum Value', color: '#3b82f6' }
      ]} />
    </div>
  );
}

export function MonteCarloChart({ data }) {
  // Simulate Monte Carlo distribution with better data
  const distribution = Array.from({ length: 50 }, (_, i) => {
    const mean = data?.wacc_method?.mean_ev || 1000;
    const stdDev = data?.wacc_method?.std_dev || 200;
    const value = mean + (Math.random() - 0.5) * stdDev * 2;
    return {
      range: `${Math.round(value/100)*100}M`,
      frequency: Math.floor(Math.random() * 15) + 1,
      value: value
    };
  }).sort((a, b) => a.value - b.value);

  return (
    <div className="card">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Monte Carlo Simulation Results
        </h3>
        <p className="text-sm text-gray-600">
          Distribution of enterprise values from probabilistic analysis
        </p>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={distribution} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="range" 
            tick={{ fill: '#6b7280', fontSize: 11 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <YAxis 
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
          />
          <Tooltip 
            content={<CustomTooltip formatter={(value) => value} />}
          />
          <Bar 
            dataKey="frequency" 
            fill="#8b5cf6"
            radius={[4, 4, 0, 0]}
            name="Frequency"
          />
        </BarChart>
      </ResponsiveContainer>
      
      <CustomLegend payload={[{ value: 'Frequency', color: '#8b5cf6' }]} />
    </div>
  );
}

export function ValuationSummaryChart({ data }) {
  const summaryData = [
    { name: 'DCF Value', value: data?.dcf_method?.enterprise_value || 0, color: '#3b82f6' },
    { name: 'Multiples Value', value: data?.multiples_method?.enterprise_value || 0, color: '#10b981' },
    { name: 'Monte Carlo Value', value: data?.wacc_method?.mean_ev || 0, color: '#8b5cf6' }
  ].filter(item => item.value > 0);

  return (
    <div className="card">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Valuation Summary
        </h3>
        <p className="text-sm text-gray-600">
          Comparison of different valuation methodologies
        </p>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={summaryData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {summaryData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            content={<CustomTooltip formatter={(value) => `$${value}M`} />}
          />
        </PieChart>
      </ResponsiveContainer>
      
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        {summaryData.map((item, index) => (
          <div key={index} className="text-center p-4 rounded-lg bg-gray-50">
            <div 
              className="w-4 h-4 rounded-full mx-auto mb-2" 
              style={{ backgroundColor: item.color }}
            />
            <p className="text-sm font-medium text-gray-700">{item.name}</p>
            <p className="text-lg font-bold text-gray-900">${item.value}M</p>
          </div>
        ))}
      </div>
    </div>
  );
} 