import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from valuation import (
    calculate_cost_of_equity, calculate_wacc, forecast_fcfs, 
    calculate_terminal_value, discount_cash_flows, discount_terminal_value
)
from montecarlo import run_monte_carlo_simulation, plot_monte_carlo_results

st.title("DCF Valuation & Monte Carlo Simulator")

# Sidebar Inputs
risk_free_rate = st.sidebar.number_input("Risk-Free Rate", 0.0, 0.2, 0.03)
beta = st.sidebar.number_input("Beta", 0.0, 2.0, 1.2)
market_risk_premium = st.sidebar.number_input("Market Risk Premium", 0.0, 0.2, 0.05)
cost_of_debt = st.sidebar.number_input("Cost of Debt", 0.0, 0.2, 0.055)
tax_rate = st.sidebar.number_input("Tax Rate", 0.0, 1.0, 0.21)
total_debt = st.sidebar.number_input("Total Debt", 0, 1_000_000_000, 500_000_000)
cash_and_equivalents = st.sidebar.number_input("Cash & Equivalents", 0, 1_000_000_000, 200_000_000)
shares_outstanding = st.sidebar.number_input("Shares Outstanding", 1, 1_000_000_000, 50_000_000)
FCF_0 = st.sidebar.number_input("FCF_0", 0, 1_000_000_000, 100_000_000)
g_exp = st.sidebar.number_input("Expected FCF Growth", 0.0, 1.0, 0.10)
n = st.sidebar.number_input("Years to Forecast", 1, 20, 5)
g_term = st.sidebar.number_input("Terminal Growth Rate", 0.0, 0.1, 0.025)
placeholder_share_price = st.sidebar.number_input("Placeholder Share Price", 0.0, 1000.0, 41.72)

# DCF & Monte Carlo configuration
num_simulations = st.sidebar.number_input("Monte Carlo Simulations", 100, 10000, 1000, step=100)

if st.button("Run Valuation"):
    # --- VALIDATIONS ---
    try:
        assert g_term < risk_free_rate + beta * market_risk_premium, \
            "Terminal growth rate must be less than cost of equity"
        assert shares_outstanding > 0, "Shares outstanding must be positive"
    except AssertionError as e:
        st.error(str(e))
        st.stop()
    
    # --- VALUATION CALCULATION ---
    cost_of_equity = calculate_cost_of_equity(risk_free_rate, beta, market_risk_premium)
    market_value_equity = shares_outstanding * placeholder_share_price
    net_debt = max(total_debt - cash_and_equivalents, 0)
    WACC = calculate_wacc(cost_of_equity, cost_of_debt, tax_rate, market_value_equity, net_debt)
    fcf_list = forecast_fcfs(FCF_0, g_exp, n)
    FCF_n = fcf_list[-1]
    TV = calculate_terminal_value(FCF_n, g_term, WACC)
    PV_FCF = discount_cash_flows(fcf_list, WACC)
    PV_TV = discount_terminal_value(TV, WACC, n)
    EV = PV_FCF + PV_TV
    equity_value = EV - net_debt
    share_price = equity_value / shares_outstanding
    
    # --- OUTPUT VALUATION RESULTS ---
    st.subheader("DCF Valuation Output")
    st.write(f"**Cost of Equity:** {cost_of_equity:.2%}")
    st.write(f"**WACC:** {WACC:.2%}")
    st.write(f"**PV of Forecasted FCFs:** ${PV_FCF:,.0f}")
    st.write(f"**PV of Terminal Value:** ${PV_TV:,.0f}")
    st.write(f"**Enterprise Value (EV):** ${EV:,.0f}")
    st.write(f"**Equity Value:** ${equity_value:,.0f}")
    st.write(f"**Implied Share Price:** ${share_price:,.2f}")
    
    # --- MONTE CARLO SIMULATION ---
    monte_carlo_config = {
        "beta": {"mean": beta, "std": 0.2, "dist": "normal"},
        "g_exp": {"mean": g_exp, "std": 0.03, "dist": "normal"},
        "g_term": {"mean": g_term, "std": 0.005, "dist": "truncated_normal"},
        "cost_of_debt": {"mean": cost_of_debt, "std": 0.01, "dist": "normal"},
        "placeholder_share_price": {"mean": placeholder_share_price, "std": 3.0, "dist": "normal"}
    }

    # Prepare function references
    sim_inputs = {
        "risk_free_rate": risk_free_rate,
        "market_risk_premium": market_risk_premium,
        "shares_outstanding": shares_outstanding,
        "FCF_0": FCF_0,
        "n": n,
        "tax_rate": tax_rate,
        "net_debt": net_debt,
        "calculate_cost_of_equity": calculate_cost_of_equity,
        "calculate_wacc": calculate_wacc,
        "forecast_fcfs": forecast_fcfs,
        "calculate_terminal_value": calculate_terminal_value,
        "discount_cash_flows": discount_cash_flows,
        "discount_terminal_value": discount_terminal_value,
    }

    df_results = run_monte_carlo_simulation(sim_inputs, monte_carlo_config, num_simulations)

    st.subheader("Monte Carlo Simulation Results")
    st.write(df_results.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])["Share Price ($)"])

    # Display histogram plot in Streamlit
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df_results["Share Price ($)"], bins=50, edgecolor='black')
    ax.set_title("Monte Carlo Simulation: Share Price Distribution")
    ax.set_xlabel("Implied Share Price ($)")
    ax.set_ylabel("Frequency")
    ax.grid(True)
    plt.tight_layout()
    st.pyplot(fig)