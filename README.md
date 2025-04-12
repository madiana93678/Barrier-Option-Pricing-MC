
# Barrier Option Pricing & Hedging - Monte Carlo Simulation

This project demonstrates the **pricing and hedging of barrier options** using Monte Carlo simulations, along with a detailed comparison to a **traditional delta hedging** strategy. The main objective of this project is to model, price, and hedge barrier options with different strategies to assess their performance. The project is implemented in Python and uses **object-oriented programming (OOP)** to structure the code.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Metrics for Comparison](#metrics-for-comparison)
6. [Results](#results)
7. [Project Structure](#project-structure)
8. [Technologies Used](#technologies-used)
9. [Future Improvements](#future-improvements)
10. [Hedging Strategies](#hedging-strategies)

## Project Overview
This project focuses on the **Monte Carlo simulation** technique for the pricing and hedging of **barrier options**. It includes:
- A class-based design using **object-oriented programming** for modularity and reusability.
- Two strategies for hedging the option: **normal delta hedging** and **Monte Carlo-based delta hedging**.
- Performance comparison of both strategies based on important **hedging metrics** such as mean error, standard deviation, skewness, and kurtosis.
- Visualizations of simulated price paths and the error distribution of both hedging strategies.

The project is aimed at individuals with a background in **finance**, **quantitative finance**, and **computer science**, especially those looking for a way to showcase their ability to combine **finance theory** with **programming skills**.

## Features
- **Barrier Option Pricing**: Implemented using Monte Carlo simulations to simulate multiple price paths and compute the expected payoff.
- **Delta Hedging**: Two strategies:
  - **Normal delta hedging** (with rebalancing at every time step).
  - **Monte Carlo-based delta hedging** (dynamic rebalancing using simulations).
- **Error Metrics**: Calculation of key metrics such as mean error, standard deviation, skewness, and kurtosis to compare the performance of both hedging strategies.
- **Visualizations**: Side-by-side histograms to compare the **hedging error distribution** of both strategies, as well as the **simulated price paths** of the underlying asset.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/madiana93678/Barrier-Option-Pricing-MC.git
   ```

2. Install the required dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

   Dependencies include:
   - `numpy`
   - `scipy`
   - `matplotlib`

## Usage

### 1. Run the Project

After installing the required dependencies, run the `main.py` script to execute the entire workflow:

```bash
python main.py
```

This will:
- Simulate multiple paths of the underlying asset using **Monte Carlo simulations**.
- Calculate the hedging errors for both the **normal delta hedging strategy** and the **Monte Carlo-based delta hedging strategy**.
- Output the **hedging error metrics** for both strategies.
- Display **side-by-side visualizations** of the error distributions for comparison.

### 2. Customization

You can easily modify the input parameters to test different scenarios:
- **Option type**: `call` or `put`.
- **Knock-in or Knock-out barrier options**.
- **Initial spot price (S)**, **strike price (K)**, **barrier price (B)**, **maturity (T)**, **interest rate (r)**, and **volatility (sigma)**.

### Example:

```python
# Example usage with a custom configuration
option_type = 'call'
knock_in = True
up = True
S = 100
K = 110
B = 120
T = 1
r = 0.05
sigma = 0.2
N = 100
M = 1000
```
## Hedging Strategies

### **1. Normal Delta Hedging Strategy**
The **Normal Delta Hedging** strategy is a classical approach used to replicate the payoff of an option by dynamically adjusting the portfolio's delta at each time step. This strategy involves the following key steps:

- **Delta Calculation**: Delta is calculated using the **Black-Scholes model**, which estimates how sensitive the option's price is to changes in the underlying asset’s price. For barrier options, the Black-Scholes formula is **adapted** by incorporating the **probability of activation** (for knock-in options) or **probability of deactivation** (for knock-out options).

    - For **knock-in options**, the **probability of activation** is calculated using the **standard Black-Scholes formula**, with an additional adjustment that takes into account the likelihood of the barrier being breached.
    
    - For **knock-out options**, the formula is adjusted to account for the **probability of the option remaining inactive** (i.e., the barrier is never breached).
    
    The delta is then calculated based on this adapted Black-Scholes model.

- **Portfolio Adjustment**: At each time step, the portfolio is rebalanced to match the **current delta** of the option. This involves buying or selling the underlying asset in order to maintain a position that is consistent with the option’s delta. The goal is to keep the portfolio neutral to small changes in the underlying asset’s price.

- **Rebalancing Frequency**: In this strategy, the portfolio is rebalanced **at each time step**, ensuring that the portfolio always reflects the most current delta.

The main advantage of the **Normal Delta Hedging Strategy** is that it is relatively **simple** and **computationally inexpensive**. However, it may not work well for more complex **path-dependent options** like **barrier options**, because it does not account for the changes in delta that might occur when the asset price is near the barrier or experiences large fluctuations. As a result, it can sometimes lead to large hedging errors.

### **2. Monte Carlo-based Delta Hedging Strategy**
The **Monte Carlo-based Delta Hedging Strategy** is an advanced approach that uses **Monte Carlo simulations** to dynamically adjust the portfolio’s delta in response to multiple simulated future price paths. This strategy involves the following steps:

- **Simulating Price Paths**: The Monte Carlo simulation generates a large number of potential price paths for the underlying asset. These paths are generated using **geometric Brownian motion**, which is the same model used in the Black-Scholes formula, but with randomness introduced to account for uncertainty in the asset price’s future behavior.

- **Delta Calculation at Every Time Step**: At each step along the simulated paths, **delta** is recalculated based on the price of the underlying asset and the time to maturity. The calculation uses the **Black-Scholes adapted formula** for barrier options, which accounts for the **probability of activation** (for knock-in options) or **probability of deactivation** (for knock-out options) in addition to the standard Black-Scholes delta formula.

    - The formula for **delta** is adjusted by the **probability of barrier activation** or **deactivation** depending on whether it's a knock-in or knock-out option.

- **Dynamic Rebalancing**: Unlike the normal strategy, the **Monte Carlo strategy** allows for **more frequent rebalancing** based on the evolution of each simulated path. The portfolio is adjusted continuously at each time step to reflect the current delta. The rebalancing is more flexible and adapts to volatility and asset price movements, especially as the price approaches the barrier.

- **Monte Carlo Simulation**: The main benefit of the Monte Carlo approach is that it allows for a much **more dynamic response** to changes in the price path. By simulating multiple paths, it accounts for the **path-dependence** of barrier options and adjusts the portfolio based on the underlying asset's price trajectory.

While the **Monte Carlo-based Hedging Strategy** is **computationally more expensive** than the normal strategy, it provides **better accuracy** by allowing for more flexible and responsive rebalancing. It can be particularly useful in hedging **path-dependent options** like **barrier options**, where the payoff is contingent on the underlying asset’s price reaching certain levels (barriers) at any point in time.

## Metrics for Comparison

We compute several important metrics to evaluate the effectiveness of both hedging strategies:

- **Mean Hedging Error**: The average deviation between the portfolio value and the actual option payoff.
- **Standard Deviation of Hedging Error**: The variability of hedging errors, indicating the stability of the hedging strategy.
- **Maximum and Minimum Hedging Error**: The largest and smallest deviations in the hedging error, respectively.
- **Skewness**: Measures the asymmetry of the error distribution (whether the hedging tends to overestimate or underestimate the payoff).
- **Kurtosis**: Measures the "tailedness" of the distribution, i.e., how likely large deviations are.

## Results

The results provide a comparison of the **normal delta hedging strategy** and the **Monte Carlo-based delta hedging strategy**. Key results include:

- **Monte Carlo strategy** tends to have a more **concentrated error distribution** around zero, indicating better hedging accuracy compared to the normal strategy.
- **Normal strategy** might show larger **hedging errors** (both positive and negative), especially in volatile scenarios.

### Example of Output:
For both strategies, the following metrics are calculated and printed:
- **Mean Hedging Error**: `-6.4791` (Normal) vs `-6.2288` (Monte Carlo)
- **Standard Deviation of Hedging Error**: `4.0545` (Normal) vs `4.3461` (Monte Carlo)
- **Max Hedging Error**: `-1.8809` (Normal) vs `-1.4564` (Monte Carlo)
- **Skewness**: `-0.5744` (Normal) vs `-0.6391` (Monte Carlo)
- **Kurtosis**: `-1.1063` (Normal) vs `-1.0528` (Monte Carlo)

## Project Structure

```
/barrier-option-hedging
│
├── main.py                  # Main execution script
├── BarrierOption.py         # Class for simulating and pricing barrier options
├── DeltaHedger.py           # Class for implementing normal delta hedging
├── MonteCarloHedger.py      # Class for implementing Monte Carlo-based hedging
├── requirements.txt         # List of dependencies
├── README.md                # Project documentation
```

## Technologies Used
- **Python**: The main programming language used for this project.
- **NumPy**: For efficient numerical computations.
- **SciPy**: For statistical functions (e.g., normal distribution).
- **Matplotlib**: For plotting and visualization of results.

## Future Improvements
- **Transaction Costs**: Introduce a cost for each trade to make the hedging strategies more realistic.
- **Stochastic Volatility**: Implement models such as the **Heston model** to account for volatility changes over time.
- **Advanced Hedging Techniques**: Explore the use of **Gamma** and **Vega** for more advanced hedging strategies.

