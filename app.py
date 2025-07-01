# app.py

import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt

from params import ValuationParams
from valuation import calc_dcf_series, calc_apv
from montecarlo import run_monte_carlo
from multiples import run_multiples_analysis
from scenario import run_scenarios
from sensitivity import run_sensitivity_analysis

st.set_page_config(page_title="Valuation Engine", layout="wide")
st.title("📊 Valuation Engine")

# --- STEP 1: Setup form ---
with st.form("setup"):
    st.header("1️⃣ Choose Analyses")
    input_mode = st.radio(
        "Cash-flow input mode:",
        ["Drivers (revenue/margins/etc.)", "Direct FCF series"]
    )
    dcf_methods = st.multiselect(
        "DCF methods to run:", 
        ["WACC", "APV"], 
        default=["WACC"]
    )
    do_mc   = st.checkbox("Monte Carlo")
    do_mult = st.checkbox("Multiples")
    do_scen = st.checkbox("Scenarios")
    do_sens = st.checkbox("Sensitivity")
    setup_submitted = st.form_submit_button("Next →")

if not setup_submitted:
    st.stop()

# --- STEP 2: Inputs for chosen analyses ---
st.header("2️⃣ Enter Inputs")

# 2a) Cash-flow inputs
if input_mode.startswith("Drivers"):
    revenue      = st.text_input("Revenue series (comma-sep)", "100,110,120")
    capex        = st.text_input("CapEx series (comma-sep)",  "10,11,12")
    depreciation = st.text_input("Depreciation series (comma-sep)", "5,6,7")
    nwc_changes  = st.text_input("NWC Changes series (comma-sep)", "2,2,2")
else:
    fcf_series = st.text_input("Free Cash Flow series (comma-sep)", "50,55,60")

# 2b) Core assumptions
wacc           = st.number_input("WACC (decimal)", 0.0, 1.0, 0.10, 0.005)
tax_rate       = st.number_input("Tax rate (decimal)", 0.0, 1.0, 0.21, 0.005)
terminal_growth= st.number_input("Terminal growth (decimal)", 0.0, 1.0, 0.02, 0.005)
share_count    = st.number_input("Share count", 1.0, 1e12, 1.0, 1.0)
cost_of_debt   = st.number_input("Cost of debt (0 = WACC)", 0.0, 1.0, 0.0, 0.005)

# 2c) Module-specific inputs
debt_schedule = {}
if "APV" in dcf_methods:
    ds = st.text_area("Debt schedule (JSON year→amount)", '{"0":0}')
    try:
        debt_schedule = {int(k):float(v) for k,v in json.loads(ds).items()}
    except:
        st.error("Invalid debt schedule JSON")

mc_specs = {}
if do_mc:
    ms = st.text_area("Monte Carlo specs (JSON)", 
                      '{"wacc":{"dist":"normal","params":{"loc":0.10,"scale":0.01}}}')
    try:
        mc_specs = json.loads(ms)
    except:
        st.error("Invalid MC specs JSON")

comps_file = None
if do_mult:
    comps_file = st.file_uploader("Peer Comps CSV", type="csv")

scenarios = {}
if do_scen:
    sj = st.text_area("Scenarios (JSON)", '{"Base":{}}')
    try:
        scenarios = json.loads(sj)
    except:
        st.error("Invalid Scenarios JSON")

sensitivity = {}
if do_sens:
    ss = st.text_area("Sensitivity ranges (JSON)", '{"wacc":[0.08,0.10,0.12]}')
    try:
        sensitivity = json.loads(ss)
    except:
        st.error("Invalid Sensitivity JSON")

# --- RUN button ---
if st.button("▶️ Run Valuation"):
    # Parse series text → lists
    def to_list(txt):
        return [float(x.strip()) for x in txt.split(",") if x.strip()]
    params = ValuationParams()
    params.wacc            = wacc
    params.tax_rate        = tax_rate
    params.terminal_growth = terminal_growth
    params.share_count     = share_count
    params.cost_of_debt    = cost_of_debt
    params.debt_schedule   = debt_schedule
    params.variable_specs  = mc_specs
    params.scenarios       = scenarios
    params.sensitivity_ranges = sensitivity

    if input_mode.startswith("Drivers"):
        params.revenue      = to_list(revenue)
        params.capex        = to_list(capex)
        params.depreciation = to_list(depreciation)
        params.nwc_changes  = to_list(nwc_changes)
    else:
        params.fcf_series   = to_list(fcf_series)

    # 1) DCF outputs
    st.subheader("📈 DCF Results")
    rows = []
    if "WACC" in dcf_methods:
        ev, eq, ps = calc_dcf_series(params)
        rows.append({"Method":"WACC DCF", "EV":ev, "Equity":eq, "PS":ps})
    if "APV" in dcf_methods:
        ev, eq, ps = calc_apv(params)
        rows.append({"Method":"APV",      "EV":ev, "Equity":eq, "PS":ps})
    st.table(pd.DataFrame(rows))

    # 2) Monte Carlo
    if do_mc:
        with st.spinner("Running Monte Carlo…"):
            mc = run_monte_carlo(params)
        st.subheader("🎲 Monte Carlo (WACC EV)")
        df_mc = mc["WACC"]
        st.write(df_mc["EV"].describe())
        fig, ax = plt.subplots()
        ax.hist(df_mc["EV"], bins=30)
        ax.set_xlabel("EV"); ax.set_ylabel("Freq")
        st.pyplot(fig)

    # 3) Multiples
    if do_mult and comps_file:
        comps = pd.read_csv(comps_file)
        mv = run_multiples_analysis(params, comps)
        st.subheader("📊 Multiples")
        st.table(mv)

    # 4) Scenarios
    if do_scen:
        sc = run_scenarios(params)
        st.subheader("🔮 Scenarios")
        st.table(sc)

    # 5) Sensitivity
    if do_sens:
        sd = run_sensitivity_analysis(params)
        st.subheader("🔍 Sensitivity")
        st.table(sd)
        # tornado for first param
        first = next(iter(sensitivity), None)
        if first:
            fig2, ax2 = plt.subplots()
            ax2.barh([str(v) for v in sensitivity[first]], sd[first])
            ax2.set_xlabel("EV"); ax2.set_title(f"Sensitivity: {first}")
            st.pyplot(fig2)

    st.success("✅ Done!")
