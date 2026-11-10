# -*- coding: utf-8 -*-
"""
Barrier option: path simulation, payoff, Monte Carlo pricing and closed-form pricing.

Closed-form prices use the Reiner-Rubinstein (1991) formulas for a continuously
monitored barrier (no dividends, no rebate). Because the simulation monitors the
barrier only at discrete dates, the barrier is shifted with the Broadie-Glasserman-Kou
(1997) continuity correction so that the closed form matches the discrete contract.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

BGK_BETA = 0.5826  # -zeta(1/2) / sqrt(2*pi), Broadie-Glasserman-Kou constant


def bs_price(option_type, S, K, tau, r, sigma):
    """Black-Scholes price of a vanilla European option (vectorised in S and tau)."""
    S = np.asarray(S, dtype=float)
    tau = np.maximum(tau, 1e-12)
    sq = sigma * np.sqrt(tau)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * tau) / sq
    d2 = d1 - sq
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * tau) * norm.cdf(d2)
    return K * np.exp(-r * tau) * norm.cdf(-d2) - S * norm.cdf(-d1)


def bs_delta(option_type, S, K, tau, r, sigma):
    """Black-Scholes delta of a vanilla European option."""
    S = np.asarray(S, dtype=float)
    tau = np.maximum(tau, 1e-12)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * tau) / (sigma * np.sqrt(tau))
    return norm.cdf(d1) if option_type == "call" else norm.cdf(d1) - 1.0


def barrier_price(option_type, knock_in, up, S, K, H, tau, r, sigma):
    """
    Reiner-Rubinstein closed-form price of a continuously monitored barrier option
    (no dividend, no rebate), vectorised in S.

    Knock-out options are priced directly; knock-in options use in-out parity
    (knock-in = vanilla - knock-out). If the spot is already beyond the barrier,
    a knock-out is worth 0 and a knock-in is worth the vanilla.
    """
    S = np.asarray(S, dtype=float)
    tau = max(float(tau), 1e-12)
    phi = 1.0 if option_type == "call" else -1.0
    eta = -1.0 if up else 1.0

    sq = sigma * np.sqrt(tau)
    mu = (r - 0.5 * sigma ** 2) / sigma ** 2
    disc = np.exp(-r * tau)

    x1 = np.log(S / K) / sq + (1 + mu) * sq
    x2 = np.log(S / H) / sq + (1 + mu) * sq
    y1 = np.log(H ** 2 / (S * K)) / sq + (1 + mu) * sq
    y2 = np.log(H / S) / sq + (1 + mu) * sq
    hs1 = (H / S) ** (2 * (mu + 1))
    hs0 = (H / S) ** (2 * mu)

    A = phi * S * norm.cdf(phi * x1) - phi * K * disc * norm.cdf(phi * x1 - phi * sq)
    B = phi * S * norm.cdf(phi * x2) - phi * K * disc * norm.cdf(phi * x2 - phi * sq)
    C = phi * S * hs1 * norm.cdf(eta * y1) - phi * K * disc * hs0 * norm.cdf(eta * y1 - eta * sq)
    D = phi * S * hs1 * norm.cdf(eta * y2) - phi * K * disc * hs0 * norm.cdf(eta * y2 - eta * sq)

    k_above = K > H
    if option_type == "call" and not up:      # down-and-out call
        out = A - C if k_above else B - D
    elif option_type == "call" and up:        # up-and-out call
        out = np.zeros_like(S) if k_above else A - B + C - D
    elif option_type == "put" and not up:     # down-and-out put
        out = A - B + C - D if k_above else np.zeros_like(S)
    else:                                     # up-and-out put
        out = B - D if k_above else A - C

    breached = (S >= H) if up else (S <= H)
    out = np.where(breached, 0.0, np.maximum(out, 0.0))
    if knock_in:
        return bs_price(option_type, S, K, tau, r, sigma) - out
    return out


class BarrierOption:

    def __init__(self, option_type, knock_in, up, S, K, B, T, r, sigma, N, M):
        """
        Parameters:
            option_type (str): 'call' or 'put'.
            knock_in (bool): True for knock-in, False for knock-out.
            up (bool): True for an up barrier, False for a down barrier.
            S (float): Spot price of the underlying asset.
            K (float): Strike price.
            B (float): Barrier level.
            T (float): Time to maturity (in years).
            r (float): Risk-free rate (continuously compounded).
            sigma (float): Volatility of the underlying asset.
            N (int): Number of time steps (barrier monitoring and rebalancing dates).
            M (int): Number of simulated paths.
        """
        assert option_type in ["call", "put"], "option_type must be 'call' or 'put'"
        assert B > 0 and K > 0 and S > 0, "Prices must be positive"
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
        self.dt = T / N

    # ------------------------------------------------------------------ simulation
    def simulate_paths(self, M=None, seed=None):
        """Simulates GBM paths under the risk-neutral measure. Returns an (M x N+1) array."""
        M = self.M if M is None else M
        rng = np.random.default_rng(seed)
        Z = rng.standard_normal((M, self.N))
        log_inc = (self.r - 0.5 * self.sigma ** 2) * self.dt + self.sigma * np.sqrt(self.dt) * Z
        log_paths = np.concatenate([np.zeros((M, 1)), np.cumsum(log_inc, axis=1)], axis=1)
        return self.S * np.exp(log_paths)

    # -------------------------------------------------------------------- barrier
    def hit(self, prices):
        """True where prices are at or beyond the barrier (element-wise)."""
        return prices >= self.B if self.up else prices <= self.B

    def is_active(self, paths):
        """
        For each path, True if the option is alive at maturity:
        knock-in -> barrier touched at least once; knock-out -> barrier never touched.
        Accepts a single path (1D) or a matrix of paths (2D).
        """
        touched = self.hit(np.atleast_2d(paths)).any(axis=1)
        active = touched if self.knock_in else ~touched
        return active if np.ndim(paths) > 1 else bool(active[0])

    def vanilla_payoff(self, final_price):
        if self.option_type == "call":
            return np.maximum(final_price - self.K, 0.0)
        return np.maximum(self.K - final_price, 0.0)

    def payoff(self, paths):
        """Barrier payoff for each path: vanilla payoff if active at maturity, 0 otherwise."""
        paths = np.atleast_2d(paths)
        return np.where(self.is_active(paths), self.vanilla_payoff(paths[:, -1]), 0.0)

    # -------------------------------------------------------------------- pricing
    def pricing(self, paths=None, seed=None):
        """
        Monte Carlo price (discretely monitored barrier).
        Returns (price, standard error).
        """
        if paths is None:
            paths = self.simulate_paths(seed=seed)
        disc_payoffs = np.exp(-self.r * self.T) * self.payoff(paths)
        return disc_payoffs.mean(), disc_payoffs.std(ddof=1) / np.sqrt(len(disc_payoffs))

    def effective_barrier(self):
        """Barrier shifted with the BGK correction for discrete monitoring every dt."""
        shift = np.exp(BGK_BETA * self.sigma * np.sqrt(self.dt))
        return self.B * shift if self.up else self.B / shift

    def analytical_price(self, S=None, tau=None, discrete=True):
        """Closed-form price (with BGK correction if discrete=True), vectorised in S."""
        S = self.S if S is None else S
        tau = self.T if tau is None else tau
        H = self.effective_barrier() if discrete else self.B
        return barrier_price(self.option_type, self.knock_in, self.up,
                             S, self.K, H, tau, self.r, self.sigma)

    # ----------------------------------------------------------------- plotting
    def plot_paths(self, n_paths=10, seed=None):
        """Plots simulated paths; red = barrier touched, blue = not touched."""
        paths = self.simulate_paths(M=n_paths, seed=seed)
        touched = self.hit(paths).any(axis=1)

        plt.figure(figsize=(10, 6))
        for i, path in enumerate(paths):
            plt.plot(path, alpha=0.7, color="red" if touched[i] else "blue")
        plt.axhline(self.B, color="black", linestyle="--", label=f"Barrier = {self.B}")
        kind = "Knock-In" if self.knock_in else "Knock-Out"
        plt.title(f"Simulated Paths - {self.option_type.upper()} {kind} (red = barrier touched)")
        plt.xlabel("Time Steps")
        plt.ylabel("Price")
        plt.grid(True)
        plt.legend()
        plt.show()
