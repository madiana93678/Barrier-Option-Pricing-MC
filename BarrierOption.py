# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from math import exp, sqrt


class BarrierOption:

    def __init__(self, option_type, knock_in, up, S, K, B, T, r, sigma, N, M):

        """
        Initializes the Barrier Option with necessary parameters.

        Parameters:
            option_type (str): 'call' or 'put'.
            knock_in (bool): True for knock-in, False for knock-out.
            up (bool): True for up barrier, False for down barrier.
            S (float): Spot price of the underlying asset.
            K (float): Strike price.
            B (float): Barrier level.
            T (float): Time to maturity (in years).
            r (float): Risk-free rate.
            sigma (float): Volatility of the underlying asset.
            N (int): Number of time steps in the simulation.
            M (int): Number of paths to simulate.
        """
        self.option_type = option_type
        self.knock_in = knock_in
        self.up = up
        self.S = S
        self.K = K
        self.B = B
        self.T = T
        self.r = r
        self.sigma = sigma
        self.N = N
        self.M = M
        self.dt = T / N  # Time step size

        # Input validation
        assert self.option_type in ["call", "put"], "option_type must be 'call' or 'put'"
        assert self.B > 0 and self.K > 0 and self.S > 0, "Prices must be positive"

    def simulate_paths(self):
        """
        Simulates multiple asset price paths using geometric Brownian motion.

        Returns:
            np.ndarray: Matrix of simulated price paths (M x N+1).
        """
        paths = np.zeros((self.M, self.N + 1))
        paths[:, 0] = self.S
        Z = np.random.normal(0, 1, (self.M, self.N))

        for k in range(1, self.N + 1):
            paths[:, k] = paths[:, k - 1] * np.exp(
                (self.r - 0.5 * self.sigma ** 2) * self.dt + self.sigma * np.sqrt(self.dt) * Z[:, k - 1]
            )
        return paths

    def is_active(self, path):
        """
        Checks if the barrier option becomes active based on the simulated path.

        Parameters:
            path (np.array): Simulated asset price path.

        Returns:
            bool: True if the option is active (knock-in) or inactive (knock-out).
        """
        for price in path:
            if (self.up and price >= self.B) or (not self.up and price <= self.B):
                return self.knock_in
        return not self.knock_in

    def payoff(self, final_price):
        """
        Computes the payoff of the option at maturity.

        Parameters:
            final_price (float): The final price of the underlying asset at maturity.

        Returns:
            float: The option payoff.
        """
        if self.option_type == 'call':
            return max(final_price - self.K, 0)
        else:
            return max(self.K - final_price, 0)

    def pricing(self):
        """
        Prices the barrier option using Monte Carlo simulation.

        Returns:
            float: The estimated price of the barrier option.
        """
        paths = self.simulate_paths()
        payoffs = np.array([self.payoff(path[-1]) for path in paths if self.is_active(path)])
        return exp(-self.r * self.T) * np.mean(payoffs)

    def plot_paths(self, n_paths=10):
        """
        Plots the simulated asset paths, showing whether the barrier was hit.

        Parameters:
            n_paths (int): Number of paths to plot.
        """
        paths = self.simulate_paths()[:n_paths]
        hit_barrier = np.array([self.is_active(path) for path in paths])

        plt.figure(figsize=(10, 6))
        for i, path in enumerate(paths):
            color = 'red' if hit_barrier[i] else 'blue'
            plt.plot(path, alpha=0.7, color=color)

        plt.axhline(self.B, color="black", linestyle="--", label=f"Barrier = {self.B}")
        plt.title(f"Simulated Paths - {self.option_type.upper()} {'Knock-In' if self.knock_in else 'Knock-Out'}")
        plt.xlabel("Time Steps")
        plt.ylabel("Price")
        plt.grid(True)
        plt.legend()
        plt.show()