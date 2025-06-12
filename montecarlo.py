import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def sample_distribution(config):
    dist = config["dist"]
    mean = config["mean"]
    std = config["std"]
    if dist == "normal":
        return np.random.normal(mean, std)
    elif dist == "lognormal":
        sigma = np.sqrt(np.log(1 + (std / mean) ** 2))
        mu = np.log(mean) - 0.5 * sigma ** 2
        return np.random.lognormal(mu, sigma)
    elif dist == "uniform":
        return np.random.uniform(mean - std, mean + std)
    elif dist == "triangular":
        return np.random.triangular(mean - std, mean, mean + std)
    elif dist == "truncated_normal":
        while True:
            x = np.random.normal(mean, std)
            if x > 0 and x < 0.05:
                return x
    else:
        raise ValueError(f"Unsupported distribution: {dist}")

def run_monte_carlo_simulation(inputs, monte_carlo_config, num_simulations):
    results = []
    for _ in range(num_simulations):
        beta_sim = sample_distribution(monte_carlo_config["beta"])
        g_exp_sim = sample_distribution(monte_carlo_config["g_exp"])
        g_term_sim = sample_distribution(monte_carlo_config["g_term"])
        cost_of_debt_sim = sample_distribution(monte_carlo_config["cost_of_debt"])
        placeholder_price_sim = sample_distribution(monte_carlo_config["placeholder_share_price"])
        if beta_sim < 0 or g_exp_sim < 0 or placeholder_price_sim <= 0:
            continue
        cost_of_equity_sim = inputs["calculate_cost_of_equity"](
            inputs["risk_free_rate"], beta_sim, inputs["market_risk_premium"]
        )
        if g_term_sim >= cost_of_equity_sim:
            continue
        market_value_equity_sim = inputs["shares_outstanding"] * placeholder_price_sim
        WACC_sim = inputs["calculate_wacc"](
            cost_of_equity_sim, cost_of_debt_sim, inputs["tax_rate"], market_value_equity_sim, inputs["net_debt"]
        )
        fcf_list_sim = inputs["forecast_fcfs"](inputs["FCF_0"], g_exp_sim, inputs["n"])
        FCF_n_sim = fcf_list_sim[-1]
        TV_sim = inputs["calculate_terminal_value"](FCF_n_sim, g_term_sim, WACC_sim)
        PV_FCF_sim = inputs["discount_cash_flows"](fcf_list_sim, WACC_sim)
        PV_TV_sim = inputs["discount_terminal_value"](TV_sim, WACC_sim, inputs["n"])
        EV_sim = PV_FCF_sim + PV_TV_sim
        equity_value_sim = EV_sim - inputs["net_debt"]
        share_price_sim = equity_value_sim / inputs["shares_outstanding"]
        results.append({
            "Beta": beta_sim,
            "g_exp": g_exp_sim,
            "g_term": g_term_sim,
            "Cost of Debt": cost_of_debt_sim,
            "WACC": WACC_sim,
            "EV ($B)": EV_sim / 1e9,
            "Equity ($B)": equity_value_sim / 1e9,
            "Share Price ($)": share_price_sim
        })
    return pd.DataFrame(results)

def plot_monte_carlo_results(df_results):
    summary_stats = df_results.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])
    print("Monte Carlo Share Price Summary:")
    print(summary_stats["Share Price ($)"])
    plt.figure(figsize=(10, 5))
    plt.hist(df_results["Share Price ($)"], bins=50, edgecolor='black')
    plt.title("Monte Carlo Simulation: Share Price Distribution")
    plt.xlabel("Implied Share Price ($)")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
