import matplotlib.pyplot as plt
from utils import compute_metrics
from BarrierOption import BarrierOption
from DeltaHedger import DeltaHedger
from MonteCarloHedger import MonteCarloHedger

if __name__ == "__main__":
    # Define option parameters
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

    # Create the barrier option instance
    barrier_option = BarrierOption(option_type, knock_in, up, S, K, B, T, r, sigma, N, M)

    # Create a Monte Carlo hedger for the option with rebalancing at every step
    monte_carlo_hedger = MonteCarloHedger(barrier_option)

    # Create a normal hedger for the option with rebalancing at every step
    normal_hedger = DeltaHedger(barrier_option)

    # Run hedging for normal strategy and plot results
    normal_errors = normal_hedger.run_hedging()

    # Run hedging for Monte Carlo strategy and plot results
    monte_carlo_errors = monte_carlo_hedger.run_hedging()

    # Calculate and print metrics for Normal Strategy
    print("\nMetrics for Normal Strategy:")
    normal_metrics = compute_metrics(normal_errors)

    # Calculate and print metrics for Monte Carlo Strategy
    print("\nMetrics for Monte Carlo Strategy:")
    monte_carlo_metrics = compute_metrics(monte_carlo_errors)


    # Create subplots to show the error distributions side-by-side
    plt.figure(figsize=(14, 6))

    # Normal strategy hedging errors plot
    plt.subplot(1, 2, 1)  # 1 row, 2 columns, first subplot
    plt.hist(normal_errors, bins=50, edgecolor='black', alpha=0.7)
    plt.title("Hedging Error Distribution for Barrier Option (Normal Strategy)")
    plt.xlabel("Hedging Error")
    plt.ylabel("Frequency")
    plt.grid(True)

    # Monte Carlo strategy hedging errors plot
    plt.subplot(1, 2, 2)  # 1 row, 2 columns, second subplot
    plt.hist(monte_carlo_errors, bins=50, edgecolor='black', alpha=0.7)
    plt.title("Hedging Error Distribution for Barrier Option (Monte Carlo Strategy)")
    plt.xlabel("Hedging Error")
    plt.ylabel("Frequency")
    plt.grid(True)

    # Show all plots in the same window
    plt.tight_layout()
    plt.show()
