import numpy as np
import matplotlib.pyplot as plt

from BarrierOption import bs_delta


class DeltaHedger:
    """
    Discrete delta hedging of a SHORT barrier option, with the analytical barrier delta.

    The hedger sells the option at t=0, receives the premium, and rebalances a
    position in the underlying at every time step, financing it through a cash
    account at the risk-free rate. At maturity:

        hedging error = (stock position * S_T + cash) - barrier payoff

    A perfect hedge gives an error of 0 on every path; with discrete rebalancing the
    errors should be centred on 0 and shrink as N grows.

    Delta used at each date:
        - barrier not touched yet: delta of the closed-form barrier price
          (Reiner-Rubinstein + BGK correction), by central finite difference;
        - barrier already touched: a knock-in has become a vanilla (Black-Scholes delta),
          a knock-out is dead (delta = 0).
    Subclasses only override `barrier_delta`.
    """

    name = "Analytical barrier delta"

    def __init__(self, option, bump=1e-3):
        """
        Parameters:
            option (BarrierOption): The barrier option to hedge.
            bump (float): Relative spot bump for the finite-difference delta.
        """
        self.option = option
        self.bump = bump

    # ------------------------------------------------------------------ deltas
    def barrier_delta(self, S, tau, t):
        """Delta of the (not yet touched) barrier option, for an array of spots S."""
        h = self.bump * S
        up = self.option.analytical_price(S + h, tau)
        down = self.option.analytical_price(S - h, tau)
        return (up - down) / (2 * h)

    def compute_delta(self, S, tau, t, touched):
        """Delta for every path at date t, given whether the barrier was already touched."""
        opt = self.option
        delta = np.zeros_like(S)
        alive = ~touched
        if alive.any():
            delta[alive] = self.barrier_delta(S[alive], tau, t)
        if touched.any() and opt.knock_in:
            delta[touched] = bs_delta(opt.option_type, S[touched], opt.K, tau, opt.r, opt.sigma)
        return delta  # knock-out already touched -> stays 0

    # ----------------------------------------------------------------- hedging
    def compute_hedging_error(self, paths, premium=None):
        """
        Simulates the hedge on each path and returns the hedging errors at maturity.

        Parameters:
            paths (np.ndarray): Simulated price paths (M x N+1).
            premium (float): Price received for the option at t=0.
                             Defaults to the closed-form price.
        """
        opt = self.option
        if premium is None:
            premium = float(opt.analytical_price())

        M, n_cols = paths.shape
        N = n_cols - 1
        growth = np.exp(opt.r * opt.dt)

        cash = np.full(M, premium)          # premium received at t=0
        stock = np.zeros(M)
        touched = np.zeros(M, dtype=bool)

        for t in range(N):
            S_t = paths[:, t]
            tau = opt.T - t * opt.dt
            touched |= opt.hit(S_t)

            if t > 0:
                cash *= growth              # interest over (t-1, t]
            delta = self.compute_delta(S_t, tau, t, touched)
            cash -= (delta - stock) * S_t   # self-financing rebalancing
            stock = delta

        cash *= growth                      # interest over the last period
        portfolio = stock * paths[:, -1] + cash
        return portfolio - opt.payoff(paths)

    def run_hedging(self, paths=None, premium=None, seed=None):
        """Runs the hedge on given paths (or freshly simulated ones) and returns the errors."""
        if paths is None:
            paths = self.option.simulate_paths(seed=seed)
        return self.compute_hedging_error(paths, premium)

    def plot_hedging_errors(self, errors):
        plt.figure(figsize=(10, 6))
        plt.hist(errors, bins=50, edgecolor="black", alpha=0.7)
        plt.title(f"Hedging Error Distribution - {self.name}")
        plt.xlabel("Hedging Error")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.show()
