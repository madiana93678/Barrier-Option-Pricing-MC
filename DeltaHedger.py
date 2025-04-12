import numpy as np
import matplotlib.pyplot as plt
from math import exp, sqrt, log
from scipy.stats import norm

class DeltaHedger:
    def __init__(self, option):
        """
        Initializes the delta hedging strategy for the given barrier option.

        Parameters:
            option (BarrierOption): The barrier option instance.
        """
        self.option = option

    def compute_delta(self, S, tau):
        """ 
        Compute the delta of a barrier option, adjusting for barrier activation and gamma hedging.

        Parameters:
            S (np.ndarray): Spot prices at all paths (M x N).
            tau (np.ndarray): Time to maturity for each time step (N x 1).
        
        Returns:
            np.ndarray: Vectorized delta for all paths and time steps (M x N).
        """
        # Avoid division by zero or invalid values
        S = np.maximum(S, 1e-10)
        tau = np.maximum(tau, 1e-10)

        # Calculate d1 and d2 for all paths and time steps (vectorized)
        d1 = (np.log(S / self.option.K) + (self.option.r + 0.5 * self.option.sigma ** 2) * tau) / (self.option.sigma * np.sqrt(tau))
        d2 = d1 - self.option.sigma * np.sqrt(tau)

        # Vanilla Black-Scholes delta for each path
        delta_vanilla = norm.cdf(d1) if self.option.option_type == "call" else norm.cdf(d1) - 1

        # Probability of barrier activation for each path
        P_activation = norm.cdf(d2)

        # Gamma hedging - adjustment to capture curvature near the barrier
        gamma = norm.pdf(d1) / (S * self.option.sigma * np.sqrt(tau))

        # Adjust delta based on knock-in or knock-out, vectorized
        if self.option.knock_in:
            delta_adjusted = delta_vanilla * P_activation + gamma
        else:
            delta_adjusted = delta_vanilla * (1 - P_activation) - gamma

        return delta_adjusted

    def compute_hedging_error(self, paths):
        """ Vectorized computation of hedging errors for all paths. """
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
        
        # Initialize portfolios
        cash = np.zeros(self.option.M)
        stock_position = np.zeros(self.option.M)

        # Loop over each time step to update portfolios
        for t in range(N):
            # Calculate delta for all paths at once
            delta = self.compute_delta(paths[:, t], tau[t])

            # Update cash and stock positions for all paths at once
            cash *= exp_rdt
            cash -= (delta - stock_position) * paths[:, t]
            stock_position = delta

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
        Run delta hedging for multiple simulated paths and compute the errors.

        Returns:
            np.ndarray: Array of hedging errors for each simulated path.
        """
        paths = self.option.simulate_paths()
        errors = self.compute_hedging_error(paths)
        return errors

    def plot_hedging_errors(self, errors):
        """ Plot the distribution of hedging errors. """
        plt.figure(figsize=(10, 6))
        plt.hist(errors, bins=50, edgecolor='black', alpha=0.7)
        plt.title("Hedging Error Distribution for Barrier Option")
        plt.xlabel("Hedging Error")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.show()
