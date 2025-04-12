import numpy as np
from math import exp, sqrt, log
from scipy.stats import norm

class MonteCarloHedger:
    def __init__(self, option):
        """
        Initializes the Monte Carlo hedging strategy for the given barrier option with rebalancing at every time step.

        Parameters:
            option (BarrierOption): The barrier option instance.
        """
        self.option = option

    def compute_delta(self, S, tau):
        """ 
        Compute the delta of a barrier option using the Black-Scholes model.

        Parameters:
            S (np.ndarray): Spot prices at all paths (M x N).
            tau (np.ndarray): Time to maturity for each time step (N x 1).
        
        Returns:
            np.ndarray: Vectorized delta for all paths and time steps (M x N).
        """
        S = np.maximum(S, 1e-10)
        tau = np.maximum(tau, 1e-10)

        d1 = (np.log(S / self.option.K) + (self.option.r + 0.5 * self.option.sigma ** 2) * tau) / (self.option.sigma * np.sqrt(tau))
        delta_vanilla = norm.cdf(d1) if self.option.option_type == "call" else norm.cdf(d1) - 1

        # Probability of barrier activation for each path
        d2 = d1 - self.option.sigma * np.sqrt(tau)
        P_activation = norm.cdf(d2)

        # Adjust delta based on knock-in or knock-out, vectorized
        if self.option.knock_in:
            return delta_vanilla * P_activation
        else:
            return delta_vanilla * (1 - P_activation)

    def compute_hedging_error(self, paths):
        """
        Monte Carlo-based computation of hedging errors for all paths, dynamically adjusting the portfolio.

        Parameters:
            paths (np.ndarray): Simulated asset price paths (M x N).

        Returns:
            np.ndarray: Hedging errors for each path (M).
        """
        dt = self.option.dt
        T = self.option.T
        r = self.option.r
        N = self.option.N
        K = self.option.K
        option_type = self.option.option_type

        # Calculate time to maturity for each time step (vectorized)
        tau = T - np.arange(N) * dt

        # Precompute the compounding factor for cash (constant across paths)
        exp_rdt = np.exp(r * dt)
        
        # Initialize portfolios (cash and stock positions)
        cash = np.zeros(self.option.M)
        stock_position = np.zeros(self.option.M)

        # Loop over each time step to dynamically adjust the portfolio
        for t in range(N):
            # Calculate delta for all paths at once
            delta = self.compute_delta(paths[:, t], tau[t])

            # Rebalance the portfolio at every time step
            cash *= exp_rdt  # Apply interest to the cash balance
            cash -= (delta - stock_position) * paths[:, t]  # Rebalance the stock position
            stock_position = delta  # Update stock position

        # Compute final payoff for all paths (vectorized)
        final_price = paths[:, -1]
        if option_type == 'call':
            payoff = np.maximum(final_price - K, 0)
        else:
            payoff = np.maximum(K - final_price, 0)

        # Hedging error (portfolio value vs option payoff)
        return (stock_position * final_price + cash) - payoff

    def run_hedging(self):
        """
        Run Monte Carlo-based delta hedging for multiple simulated paths and compute the errors.

        Returns:
            np.ndarray: Array of hedging errors for each simulated path.
        """
        paths = self.option.simulate_paths()
        errors = self.compute_hedging_error(paths)
        return errors

    def plot_hedging_errors(self, errors):
        """ Plot the distribution of hedging errors. """
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        plt.hist(errors, bins=50, edgecolor='black', alpha=0.7)
        plt.title("Hedging Error Distribution for Barrier Option (Monte Carlo with Rebalancing at Every Step)")
        plt.xlabel("Hedging Error")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.show()
