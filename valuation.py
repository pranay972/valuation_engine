import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- FUNCTIONS ---
def calculate_cost_of_equity(rf, beta, market_risk_premium):
    return rf + beta * market_risk_premium

def calculate_wacc(cost_of_equity, cost_of_debt, tax_rate, equity_value, debt_value):
    total_value = equity_value + debt_value
    weight_equity = equity_value / total_value
    weight_debt = debt_value / total_value
    return weight_equity * cost_of_equity + weight_debt * cost_of_debt * (1 - tax_rate)

def forecast_fcfs(FCF_0, g_exp, n):
    return [FCF_0 * (1 + g_exp) ** t for t in range(1, n + 1)]

def calculate_terminal_value(FCF_n, g_term, WACC):
    return FCF_n * (1 + g_term) / (WACC - g_term)

def discount_cash_flows(cash_flows, WACC):
    return sum([cf / (1 + WACC) ** (t + 1) for t, cf in enumerate(cash_flows)])

def discount_terminal_value(TV, WACC, n):
    return TV / (1 + WACC) ** n
