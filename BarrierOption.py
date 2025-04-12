# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from math import exp, sqrt


class BarrierOption:

    def __init__(self, option_type, knock_in, up, S, K, B, T, r, sigma, N, M):
        """
        Initialize the barrier option with its characteristics and simulation parameters.
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
        self.dt = T / N  # precompute dt

        assert self.option_type in ["call", "put"], "option_type must be 'call' or 'put'"
        assert self.B > 0 and self.K > 0 and self.S > 0, "Prices must be positive"

    def simulate_paths(self, n_paths):
        """
        Simulates n_paths of underlying asset prices using geometric Brownian motion.

        Parameters:
            n_paths (int): number of paths to be simulated

        Returns:
            np.ndarray: Matrix of simulated price paths of shape (n_paths, N+1)
        """
        path = np.zeros((n_paths, self.N + 1))
        path[:, 0] = self.S
        Z = np.random.normal(0, 1, (n_paths, self.N))

        for k in range(1, self.N + 1):
            path[:, k] = path[:, k - 1] * np.exp(
                (self.r - 0.5 * self.sigma ** 2) * self.dt + self.sigma * sqrt(self.dt) * Z[:, k - 1]
            )

        return path

    def is_active(self, path, return_activation_step=False):
        """
        Check if the barrier option becomes active and optionally return the activation step.

        Parameters:
            path (np.array): Price path of the underlying
            return_activation_step (bool): If True, also return the step when activation occurred

        Returns:
            bool or (bool, int): True if the option is active. If return_activation_step is True,
                                 also returns the first step where the barrier is triggered (or None)
        """
        activation_step = None

        for t in range(1, len(path)):
            S_t = path[t]
            if self.up and S_t >= self.B:
                activation_step = t
                break
            elif not self.up and S_t <= self.B:
                activation_step = t
                break

        if self.knock_in:
            is_active = activation_step is not None
        else:
            is_active = activation_step is None  # knock-out: option deactivates if barrier is hit

        if return_activation_step:
            return is_active, activation_step if is_active else None
        else:
            return is_active

    def pricing(self):
        """
        Prices the barrier option using Monte Carlo simulation.

        Returns:
            float: Discounted expected payoff of the option
        """
        paths = self.simulate_paths(self.M)

        # Use list comprehension to evaluate activation status
        valid_paths = np.array([self.is_active(path) for path in paths])

        # Compute payoff for valid paths
        if self.option_type == "call":
            payoffs = np.maximum(paths[valid_paths, -1] - self.K, 0)
        else:
            payoffs = np.maximum(self.K - paths[valid_paths, -1], 0)

        discounted_price = exp(-self.r * self.T) * np.mean(payoffs)
        return discounted_price

    def plot_paths(self, n_paths=10):
        """
        Plots simulated paths of the underlying and indicates whether the barrier is hit.

        Parameters:
            n_paths (int): Number of paths to plot
        """
        plt.figure(figsize=(10, 6))
        paths = self.simulate_paths(n_paths)

        if self.up:
            hit_barrier = (paths[:, 1:] >= self.B).any(axis=1)
        else:
            hit_barrier = (paths[:, 1:] <= self.B).any(axis=1)

        label_used = {"Active option": False, "Inactive option": False}

        for i in range(paths.shape[0]):
            hit = hit_barrier[i]
            color = "red" if hit else "blue"
            label = "Active option" if hit else "Inactive option"
            plt.plot(paths[i], alpha=0.7, color=color,
                     label=label if not label_used[label] else "")
            label_used[label] = True

        plt.axhline(self.B, color="black", linestyle="--", label=f"Barrier = {self.B}")
        plt.title(f"Simulated Paths - {self.option_type.upper()} {'Knock-In' if self.knock_in else 'Knock-Out'}")
        plt.xlabel("Time Steps")
        plt.ylabel("Price")
        plt.grid(True)
        plt.legend()
        plt.show()

    def summary(self):
        """
        Prints a summary of the barrier option’s characteristics.
        """
        print(f"Option {self.option_type.upper()} - {'Knock-In' if self.knock_in else 'Knock-Out'}")
        print(f"Spot: {self.S}, Strike: {self.K}, Barrier: {self.B}")
        print(f"Up: {self.up}, Maturity: {self.T} years, Vol: {self.sigma}, r: {self.r}")
