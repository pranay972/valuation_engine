import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from params import ValuationParams
from valuation import run_single_valuations
from montecarlo import run_monte_carlo
from multiples import run_multiples_analysis

st.set_page_config(page_title="🔍 Advanced Valuation Dashboard", layout="wide")

st.title("🔍 Advanced Valuation Dashboard")
st.markdown("A streamlined interface for DCF (WACC & APV), Monte Carlo simulation, and peer multiples analysis.")

# --- INPUT FORM ---
with st.sidebar.form("params_form", clear_on_submit=False):
    st.header("📥 Core Parameters")
    rf = st.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1,
                         help="Use the yield on 10-year government bonds")
    mkt_prem = st.number_input("Market Risk Premium (%)", min_value=0.0, max_value=10.0, value=6.0, step=0.1)
    cd = st.number_input("Cost of Debt (%)", min_value=0.0, max_value=10.0, value=4.0, step=0.1)
    tax = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=21.0, step=1.0)
    st.markdown("---")
    st.header("⚖️ Balance Sheet")
    total_debt = st.number_input("Total Debt (Billion $)", min_value=0.0, max_value=2000.0, value=100.0, step=10.0)
    cash = st.number_input("Cash & Equivalents (Billion $)", min_value=0.0, max_value=2000.0, value=50.0, step=10.0)
    shares = st.number_input("Shares Outstanding (Millions)", min_value=1.0, max_value=100000.0, value=5000.0, step=100.0)
    st.markdown("---")
    st.header("📈 Forecast Settings")
    horizon = st.slider("Forecast Horizon (years)", 1, 20, 5)
    dv_ratio = st.slider("Target D/V Ratio", 0.0, 1.0, 0.25, step=0.05)
    mid_year = st.checkbox("Use Mid-Year Discounting", True)
    fcf_mode = st.radio("FCF Input Mode", ["AUTO", "LIST"], index=0)
    base_fcf = st.number_input("Base FCF (Billion $)", min_value=0.0, max_value=500.0, value=10.0, step=1.0)
    g_exp = st.slider("Explicit Growth Rate (%)", 0.0, 30.0, 8.0, step=0.5)
    g_term = st.slider("Terminal Growth Rate (%)", 0.0, 10.0, 2.0, step=0.25)
    fcf_list = []
    if fcf_mode == "LIST":
        raw = st.text_area("Enter FCFs (comma-separated, Billion $)", ",".join([f"{base_fcf*(1+g_exp/100)**i:.1f}" for i in range(horizon)]))
        try:
            fcf_list = [float(x) for x in raw.split(",")]
        except:
            st.error("Invalid FCF list format.")

    st.markdown("---")
    st.header("🎲 Monte Carlo")
    run_mc = st.checkbox("Enable Monte Carlo", True)
    mc_runs = st.number_input("MC Iterations", min_value=100, max_value=100000, value=2000, step=100)
    submitted = st.form_submit_button("Run Analysis")

# Instantiate params
if submitted:
    params = ValuationParams(
        risk_free_rate=rf/100,
        market_risk_premium=mkt_prem/100,
        cost_of_debt=cd/100,
        tax_rate=tax/100,
        total_debt=total_debt * 1e9,
        cash_and_equivalents=cash * 1e9,
        shares_outstanding=shares * 1e6,
        n=horizon,
        target_debt_ratio=dv_ratio,
        mid_year_discount=mid_year,
        fcf_input_mode=fcf_mode,
        FCF_0=base_fcf * 1e9,
        g_exp=g_exp/100,
        g_term=g_term/100,
        fcf_list=[x * 1e9 for x in fcf_list] if fcf_list else None
    )

    # --- Single Valuation ---
    st.subheader("1️⃣ Single Valuation (WACC & APV)")
    df_single = run_single_valuations(params, ["WACC", "APV"])
    st.dataframe(df_single.style.format({
        "EV ($B)": "{:.2f}", "Equity ($B)": "{:.2f}", "Share Price ($)": "{:.2f}"
    }), height=200)

    # Breakdown PV by year for first method
    st.markdown("**Detailed Cash-Flow Breakdown (WACC)**")
    fcf = params.fcf_list if fcf_list else None
    # (Could implement extraction of PV table here... placeholder)
    st.write("*Detailed PV table will appear here.*")

    # --- Monte Carlo ---
    if run_mc:
        st.subheader("2️⃣ Monte Carlo Simulation")
        df_mc, ev_store = run_monte_carlo(params, ["WACC", "APV"], runs=int(mc_runs), seed=42)
        st.dataframe(df_mc.style.format({
            "EV Mean ($B)": "{:.2f}", "EV Median ($B)": "{:.2f}", "EV P5 ($B)": "{:.2f}", "EV P95 ($B)": "{:.2f}",
            "Price Mean ($)": "{:.2f}", "Price Median ($)": "{:.2f}", "Price P5 ($)": "{:.2f}", "Price P95 ($)": "{:.2f}"
        }), height=200)

        # Histograms
        st.markdown("**Price Distributions**")
        cols = st.columns(2)
        net_debt = params.total_debt - params.cash_and_equivalents
        for i, m in enumerate(["WACC", "APV"]):
            prices = (ev_store[m] - net_debt) / params.shares_outstanding
            with cols[i]:
                fig, ax = plt.subplots()
                ax.hist(prices, bins=30)
                ax.set_title(f"{m} Distribution")
                ax.set_xlabel("Price ($)")
                st.pyplot(fig)

    # --- Peer Multiples ---
    st.subheader("3️⃣ Peer Multiples Analysis")
    df_mult = run_multiples_analysis(params)
    st.dataframe(df_mult.style.format({"Mean Price ($)": "{:.2f}", "Median Price ($)": "{:.2f}"}), height=150)

else:
    st.info("🔧 Configure inputs and click **Run Analysis** to view results.")
