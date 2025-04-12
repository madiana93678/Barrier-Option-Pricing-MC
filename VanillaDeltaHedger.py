import numpy as np
from scipy.stats import norm

class VanillaDeltaHedger:
    def __init__(self, path, option, T_remaining, activation_step=0):
        """
        Initializes the vanilla delta hedging on a single path.

        Parameters:
            path (np.array): 1D array of prices from activation to maturity
            option (BarrierOption): Instance of the BarrierOption (contains K, r, sigma, etc.)
            T_remaining (float): Time to maturity from activation step
            activation_step (int): Step where the barrier was activated
        """
        self.path = path
        self.option = option
        self.T = T_remaining
        self.dt = self.T / len(path) 
        self.activation_step = activation_step

    def compute_delta(self, S, tau):
        """
        Computes the corrected delta of the barrier option as:
        Delta_barrier ≈ Delta_vanilla × P_activation
        P_activation ≈ exp( -2 * ln(S/B) * ln(K/B) / (sigma² * T) )

        Parameters:
            S (float): spot price at time t
            tau (float): time to maturity

        Returns:
            float: corrected delta
        """
        if tau <= 0 or S <= 0:
            return 0.0

        # Vanilla Black-Scholes delta
        d1 = (np.log(S / self.option.K) + (self.option.r + 0.5 * self.option.sigma ** 2) * tau) / \
            (self.option.sigma * np.sqrt(tau))
        if self.option.option_type == "call":
            delta_vanilla = norm.cdf(d1)
        else:
            delta_vanilla = norm.cdf(d1) - 1

        # Approximate hitting probability
        K, B, sigma = self.option.K, self.option.B, self.option.sigma
        try:
            num = -2 * np.log(S / B) * np.log(K / B)
            den = sigma ** 2 * tau

            # Clamp exponent to avoid overflow in exp
            exponent = np.clip(num / den, -700, 700)
            prob_hit = np.exp(exponent)

            # Clip prob to avoid 0 or 1
            prob_hit = np.clip(prob_hit, 1e-6, 1 - 1e-6)
        except:
            prob_hit = 0.0  # fallback in case of math error

        # Apply knock-in / knock-out adjustment
        if self.option.knock_in:
            return delta_vanilla * prob_hit
        else:
            return delta_vanilla * (1 - prob_hit)
        
    def compute_MC_delta(self, S_t, t_step, n_sim=100):
        """
        Approximates the delta using local Monte Carlo simulation from current step t.

        Parameters:
            S_t (float): Spot price at current time step
            t_step (int): Current step index (0 ≤ t_step < N)
            n_sim (int): Number of sub-paths to simulate

        Returns:
            float: Estimated delta
        """
        T = self.T
        N = len(self.path) - 1
        dt = self.dt
        t_current = t_step * dt
        tau = T - t_current
        K = self.option.K
        r = self.option.r
        sigma = self.option.sigma
        B = self.option.B
        up = self.option.up
        knock_in = self.option.knock_in
        option_type = self.option.option_type

        steps_remaining = N - t_step
        S_paths = np.zeros((n_sim, steps_remaining + 1))
        S_paths[:, 0] = S_t

        Z = np.random.normal(0, 1, (n_sim, steps_remaining))

        for i in range(1, steps_remaining + 1):
            S_paths[:, i] = S_paths[:, i - 1] * np.exp(
                (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z[:, i - 1]
            )

        # Construire les paths complets
        full_paths = S_paths  # shape (n_sim, remaining_steps + 1)

        # Calcule les payoffs en fonction du type de barrière
        payoffs = np.zeros(n_sim)

        for i in range(n_sim):
            path_i = full_paths[i]
            hit_barrier = (path_i >= B).any() if up else (path_i <= B).any()

            active = hit_barrier if knock_in else not hit_barrier

            if active:
                if option_type == "call":
                    payoffs[i] = max(path_i[-1] - K, 0)
                else:
                    payoffs[i] = max(K - path_i[-1], 0)

        # Estimation du delta via la méthode des moindres carrés
        ST = full_paths[:, -1]
        cov = np.cov(ST, payoffs, ddof=1)
        var_ST = cov[0, 0]
        cov_ST_payoff = cov[0, 1]

        if var_ST == 0:
            return 0.0

        return cov_ST_payoff / var_ST




    def run_hedging(self):
        """
        Runs the delta hedging strategy from the activation step to maturity.

        Returns:
            float: Hedging error (replication portfolio - payoff)
        """
        cash = 0.0
        stock_position = 0.0
        N = len(self.path) - 1

        for t in range(N):
            S_t = self.path[t]
            tau = self.T - t * self.dt
            delta = self.compute_MC_delta(S_t, t_step=t, n_sim=100)

            # Update cash and rebalance
            cash *= np.exp(self.option.r * self.dt)
            cash -= (delta - stock_position) * S_t
            stock_position = delta

        # Final portfolio value
        final_value = stock_position * self.path[-1] + cash

        # Compute payoff
        if self.option.option_type == "call":
            payoff = max(self.path[-1] - self.option.K, 0)
        else:
            payoff = max(self.option.K - self.path[-1], 0)

        return final_value - payoff
