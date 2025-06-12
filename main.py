import pandas as pd
from valuation import calculate_cost_of_equity, calculate_wacc, forecast_fcfs, calculate_terminal_value, discount_cash_flows, discount_terminal_value
from montecarlo import run_monte_carlo_simulation, plot_monte_carlo_results

# --- INPUTS ---
inputs = {
    "risk_free_rate": 0.03,
    "beta": 1.2,
    "market_risk_premium": 0.05,
    "cost_of_debt": 0.055,
    "tax_rate": 0.21,
    "total_debt": 500_000_000,
    "cash_and_equivalents": 200_000_000,
    "shares_outstanding": 50_000_000,
    "FCF_0": 100_000_000,
    "g_exp": 0.10,
    "n": 5,
    "g_term": 0.025,
    "placeholder_share_price": 41.72
}

# --- VALIDATIONS ---
assert inputs["g_term"] < inputs["risk_free_rate"] + inputs["beta"] * inputs["market_risk_premium"], \
    "Terminal growth rate must be less than cost of equity"
assert inputs["shares_outstanding"] > 0, "Shares outstanding must be positive"

# --- VALUATION CALCULATION ---
cost_of_equity = calculate_cost_of_equity(inputs["risk_free_rate"], inputs["beta"], inputs["market_risk_premium"])
market_value_equity = inputs["shares_outstanding"] * inputs["placeholder_share_price"]
net_debt = max(inputs["total_debt"] - inputs["cash_and_equivalents"], 0)
WACC = calculate_wacc(cost_of_equity, inputs["cost_of_debt"], inputs["tax_rate"], market_value_equity, net_debt)
fcf_list = forecast_fcfs(inputs["FCF_0"], inputs["g_exp"], inputs["n"])
FCF_n = fcf_list[-1]
TV = calculate_terminal_value(FCF_n, inputs["g_term"], WACC)
PV_FCF = discount_cash_flows(fcf_list, WACC)
PV_TV = discount_terminal_value(TV, WACC, inputs["n"])
EV = PV_FCF + PV_TV
equity_value = EV - net_debt
share_price = equity_value / inputs["shares_outstanding"]

# --- OUTPUT VALUATION RESULTS ---
print("==== DCF Valuation Output ====")
print(f"Cost of Equity: {cost_of_equity:.2%}")
print(f"WACC: {WACC:.2%}")
print(f"PV of Forecasted FCFs: ${PV_FCF:,.0f}")
print(f"PV of Terminal Value: ${PV_TV:,.0f}")
print(f"Enterprise Value (EV): ${EV:,.0f}")
print(f"Equity Value: ${equity_value:,.0f}")
print(f"Implied Share Price: ${share_price:,.2f}")

# --- MONTE CARLO SIMULATION ---
num_simulations = 1000
monte_carlo_config = {
    "beta": {"mean": 1.2, "std": 0.2, "dist": "normal"},
    "g_exp": {"mean": 0.10, "std": 0.03, "dist": "normal"},
    "g_term": {"mean": 0.025, "std": 0.005, "dist": "truncated_normal"},
    "cost_of_debt": {"mean": 0.055, "std": 0.01, "dist": "normal"},
    "placeholder_share_price": {"mean": 41.72, "std": 3.0, "dist": "normal"}
}

inputs.update({
    "calculate_cost_of_equity": calculate_cost_of_equity,
    "calculate_wacc": calculate_wacc,
    "forecast_fcfs": forecast_fcfs,
    "calculate_terminal_value": calculate_terminal_value,
    "discount_cash_flows": discount_cash_flows,
    "discount_terminal_value": discount_terminal_value,
    "net_debt": net_debt
})

df_results = run_monte_carlo_simulation(inputs, monte_carlo_config, num_simulations)
plot_monte_carlo_results(df_results)
