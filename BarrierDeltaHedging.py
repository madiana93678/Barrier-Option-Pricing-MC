import numpy as np
from VanillaDeltaHedger import VanillaDeltaHedger

class BarrierDeltaHedger:
    def __init__(self, barrier_option):
        """
        Initializes the barrier delta hedger.

        Parameters:
            barrier_option (BarrierOption): An instance of the BarrierOption class.
        """
        self.option = barrier_option

    def hedge_single_path(self, path):
        """
        Runs delta hedging on a single path, starting only when the option is active.

        Parameters:
            path (np.ndarray): A single simulated price path

        Returns:
            float: Hedging error (replication portfolio - payoff)
        """
        is_active, activation_step = self.option.is_active(path, return_activation_step=True)

        if not is_active:
            return 0.0

        hedging_path = path[activation_step:]
        time_remaining = self.option.T - activation_step * self.option.dt

        vanilla_hedger = VanillaDeltaHedger(
            hedging_path,
            self.option,
            time_remaining,
            activation_step=activation_step
        )
        return vanilla_hedger.run_hedging()

    def run_barrier_hedging(self):
        """
        Runs the barrier-aware delta hedging simulation on all paths.

        Returns:
            np.ndarray: Array of hedging errors for each path
        """
        paths = self.option.simulate_paths(self.option.M)
        errors = [self.hedge_single_path(path) for path in paths]
        return np.array(errors)

    def plot_hedging_errors(self, errors):
        """
        Plots a histogram of hedging errors.

        Parameters:
            errors (np.ndarray): Array of hedging errors
        """
        import matplotlib.pyplot as plt
        plt.figure(figsize=(8, 5))
        plt.hist(errors, bins=50, edgecolor="black")
        plt.title("Hedging Error Distribution - Barrier Option")
        plt.xlabel("Error")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.show()
