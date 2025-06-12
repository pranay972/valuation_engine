# DCF Valuation and Monte Carlo Simulation

This project implements a discounted cash flow (DCF) valuation model with a Monte Carlo simulation to estimate share price uncertainty. It uses both Python scripts and a Jupyter Notebook for interactive exploration.

## Project Structure

- **[main.py](main.py)**  
  Main script which sets up inputs, performs validations, calculates valuation metrics (e.g., cost of equity, WACC, enterprise value, etc.), and runs the Monte Carlo simulation.

- **[valuation.py](valuation.py)**  
  Contains the valuation functions:  
  - `calculate_cost_of_equity`  
  - `calculate_wacc`  
  - `forecast_fcfs`  
  - `calculate_terminal_value`  
  - `discount_cash_flows`  
  - `discount_terminal_value`

- **[montecarlo.py](montecarlo.py)**  
  Implements the Monte Carlo simulation logic to stress-test the valuation model.

- **[valuation.ipynb](valuation.ipynb)**  
  A Jupyter Notebook that walks through the valuation steps and the simulation process interactively.

- **[requirements.txt](requirements.txt)**  
  Lists the required dependencies: `pandas`, `numpy`, and `matplotlib`.

## Setup

1. **Install Dependencies**

   Run the following command to install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Inputs**

   The inputs for the valuation and simulation are defined in [main.py](main.py) and [valuation.ipynb](valuation.ipynb). Adjust values as needed:
   
   - Risk free rate, beta, market risk premium, etc.
   - Forecasted Free Cash Flow (`FCF_0`), expected growth (`g_exp`), terminal growth (`g_term`), etc.

## Running the Model

- **Run the Valuation in Script Mode**

  Execute [main.py](main.py) to calculate the DCF valuation and run the Monte Carlo simulation:

  ```bash
  python main.py
  ```

- **Interactive Analysis**

  Open [valuation.ipynb](valuation.ipynb) in Jupyter Notebook or JupyterLab to explore and visualize the steps interactively.

## Overview of Key Functions

- **Calculation Functions**  
  See [valuation.py](valuation.py) for functions like [`calculate_cost_of_equity`](valuation.py#L0) and [`calculate_wacc`](valuation.py#L0).

- **Monte Carlo Simulation**  
  Simulation is implemented in [montecarlo.py](montecarlo.py) where inputs are sampled and valuation is performed repeatedly.

## Output

The model prints key metrics including:
- Cost of Equity
- WACC
- Present values of FCFs and Terminal Value
- Enterprise Value
- Equity Value
- Implied Share Price

Additionally, the simulation results are visualized with histograms in both the script and notebook.
