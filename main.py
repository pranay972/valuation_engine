import matplotlib.pyplot as plt
from params import ValuationParams
from valuation import run_single_valuations
from montecarlo import run_monte_carlo
from multiples import run_multiples_analysis


def main():
    params = ValuationParams()
    methods = ['WACC','APV']

    # Single
    df_single = run_single_valuations(params, methods)
    print(df_single.to_string(index=False))

    # Monte Carlo
    df_mc, ev_store = run_monte_carlo(params, methods)
    print(df_mc.to_string(index=False))
    for m, evs in ev_store.items():
        prices = (evs - (params.total_debt-params.cash_and_equivalents)) / params.shares_outstanding
        plt.hist(prices, bins=30)
        plt.title(f"{m} Price Dist")
        plt.show()

    # Multiples
    df_mult = run_multiples_analysis(params)
    print(df_mult.to_string(index=False))

if __name__ == '__main__':
    main()
