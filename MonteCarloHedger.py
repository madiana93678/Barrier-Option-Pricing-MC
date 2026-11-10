import numpy as np

from DeltaHedger import DeltaHedger


class MonteCarloHedger(DeltaHedger):
    """
    Delta hedging with a Monte Carlo delta (no closed-form formula needed).

    At each rebalancing date and for each path whose barrier has not been touched,
    the option is revalued by simulating `n_sim` sub-paths from S*(1+h) and S*(1-h)
    with the SAME random numbers (common random numbers), and

        delta = (V(S*(1+h)) - V(S*(1-h))) / (2*h*S)

    The barrier is monitored on the same discrete grid as the main simulation, so
    this delta targets exactly the contract being hedged. Since S_u = S_t * exp(X_u),
    a sub-path touches the barrier iff S_t * max(exp(X)) >= B (up barrier), which lets
    every path share the same simulated sub-paths and keeps the computation vectorised.

    This approach generalises to payoffs without a closed form, at the cost of
    Monte Carlo noise in the delta.
    """

    name = "Monte Carlo delta"

    def __init__(self, option, n_sim=500, bump=0.01, seed=None):
        """
        Parameters:
            option (BarrierOption): The barrier option to hedge.
            n_sim (int): Number of sub-paths used for each delta estimate.
            bump (float): Relative spot bump (larger than for the analytical delta,
                          because the barrier indicator makes the MC price non-smooth).
            seed (int): Seed for reproducibility.
        """
        super().__init__(option, bump=bump)
        self.n_sim = n_sim
        self.rng = np.random.default_rng(seed)

    def barrier_delta(self, S, tau, t):
        opt = self.option
        steps = opt.N - t                               # remaining monitoring dates
        Z = self.rng.standard_normal((self.n_sim, steps))
        X = np.cumsum((opt.r - 0.5 * opt.sigma ** 2) * opt.dt
                      + opt.sigma * np.sqrt(opt.dt) * Z, axis=1)
        X_T = X[:, -1]
        X_ext = X.max(axis=1) if opt.up else X.min(axis=1)
        disc = np.exp(-opt.r * steps * opt.dt)

        def value(spot):
            spot = spot[:, None]                        # (paths, 1) x (1, n_sim)
            touched = opt.hit(spot * np.exp(X_ext)[None, :])
            alive = touched if opt.knock_in else ~touched
            payoff = opt.vanilla_payoff(spot * np.exp(X_T)[None, :])
            return disc * (payoff * alive).mean(axis=1)

        h = self.bump * S
        return (value(S + h) - value(S - h)) / (2 * h)
