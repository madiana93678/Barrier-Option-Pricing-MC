
import matplotlib.pyplot as plt
import numpy as np

from BarrierOption import BarrierOption
from DeltaHedger import DeltaHedger
from MonteCarloHedger import MonteCarloHedger
from VanillaDeltaHedger import VanillaDeltaHedger
from utils import compute_metrics

if __name__ == "__main__":
    # ------------------------------------------------------------ parameters
    option_type = "call"
    knock_in = True
    up = True
    S = 100
    K = 110
    B = 120
    T = 1
    r = 0.05
    sigma = 0.2
    N = 100      # monitoring / rebalancing dates
    M = 10000    # simulated paths
    SEED = 42

    option = BarrierOption(option_type, knock_in, up, S, K, B, T, r, sigma, N, M)

    # --------------------------------------------------------------- pricing
    paths = option.simulate_paths(seed=SEED)   # same paths for every strategy
    mc_price, mc_se = option.pricing(paths)
    cf_price = float(option.analytical_price())
    cf_cont = float(option.analytical_price(discrete=False))

    print("Pricing")
    print(f"  Monte Carlo (discrete barrier) : {mc_price:.4f}  (s.e. {mc_se:.4f})")
    print(f"  Closed form + BGK correction   : {cf_price:.4f}")
    print(f"  Closed form, continuous barrier: {cf_cont:.4f}")

    # --------------------------------------------------------------- hedging
    # The option is sold at its closed-form price; every strategy is run on the same paths.
    hedgers = [
        VanillaDeltaHedger(option),
        DeltaHedger(option),
        MonteCarloHedger(option, n_sim=500, seed=SEED),
    ]
    errors = {h.name: h.run_hedging(paths, premium=cf_price) for h in hedgers}

    for name, e in errors.items():
        compute_metrics(e, label=f"Hedging errors - {name}")

    # ----------------------------------------------------------------- plots
    lo = min(np.quantile(e, 0.005) for e in errors.values())
    hi = max(np.quantile(e, 0.995) for e in errors.values())
    bins = np.linspace(lo, hi, 60)

    fig, axes = plt.subplots(1, len(errors), figsize=(16, 5), sharex=True, sharey=True)
    for ax, (name, e) in zip(axes, errors.items()):
        ax.hist(e, bins=bins, edgecolor="black", alpha=0.7)
        ax.axvline(0, color="red", linestyle="--")
        ax.set_title(f"{name}\nmean={e.mean():.3f}, std={e.std():.3f}")
        ax.set_xlabel("Hedging error at maturity")
        ax.grid(True)
    axes[0].set_ylabel("Frequency")
    plt.suptitle("Up-and-in call: hedging error distribution by strategy")
    plt.tight_layout()
    plt.show()
