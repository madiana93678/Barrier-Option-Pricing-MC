# Barrier Option Pricing & Delta Hedging

Pricing and discrete delta hedging of European barrier options (knock-in / knock-out, up / down, call / put) under Black-Scholes, in object-oriented Python.

The project answers two questions:
1. **Pricing**: does a Monte Carlo price of a discretely monitored barrier agree with the closed-form price?
2. **Hedging**: if you sell a barrier option and delta-hedge it, how much does using a barrier-aware delta improve the hedge compared with a naive vanilla delta?

## Methodology

### Pricing
- **Monte Carlo**: risk-neutral GBM paths, barrier monitored at each of the `N` time steps, discounted barrier payoff (zero on inactive paths). Reported with its standard error.
- **Closed form**: Reiner-Rubinstein (1991) formulas for knock-out options; knock-in options via in-out parity (knock-in = vanilla − knock-out).
- **Discrete monitoring**: the closed form assumes a continuously monitored barrier, so the barrier is shifted with the Broadie-Glasserman-Kou (1997) continuity correction, `B · exp(±0.5826 σ √Δt)`.

### Hedging
The hedger **sells the option at t=0, receives the premium** and rebalances a self-financing position in the underlying at every time step, with a cash account accruing at the risk-free rate. At maturity:

```
hedging error = stock position × S_T + cash − barrier payoff
```

A perfect continuous hedge would give 0 on every path. With discrete rebalancing, the errors should be centred on 0 and shrink like `1/√N`.

Three strategies are compared **on the same simulated paths**:

| Strategy | Delta before the barrier is touched | After the barrier is touched |
|---|---|---|
| Naive vanilla delta | Black-Scholes delta of the vanilla option | knock-in: vanilla delta · knock-out: 0 |
| Analytical barrier delta | finite-difference delta of the closed-form barrier price | knock-in: vanilla delta · knock-out: 0 |
| Monte Carlo delta | bump-and-revalue Monte Carlo delta with common random numbers | knock-in: vanilla delta · knock-out: 0 |

The Monte Carlo delta needs no closed form, so it generalises to exotic payoffs. It monitors the barrier on the same discrete grid as the contract and shares sub-paths across all hedged paths, so it stays fully vectorised.

## Results

Up-and-in call, `S=100, K=110, B=120, T=1, r=5%, σ=20%`, `N=100` rebalancing dates, `M=10,000` paths, seed 42.

**Pricing**

| Method | Price |
|---|---|
| Monte Carlo (discrete barrier) | 5.733 (s.e. 0.117) |
| Closed form + BGK correction | 5.817 |
| Closed form, continuous barrier | 5.889 |

The Monte Carlo price is within one standard error of the corrected closed form. The closed-form prices were also checked against high-precision Monte Carlo (200,000 paths, daily monitoring) on down-and-out puts, up-and-out calls and down-and-in calls/puts, all within about one standard error.

**Hedging errors at maturity**

| Strategy | Mean | Std | 5% quantile | Skewness |
|---|---|---|---|---|
| Naive vanilla delta | −0.009 | 1.311 | −1.383 | 3.15 |
| Analytical barrier delta | −0.011 | **0.943** | −1.359 | −0.39 |
| Monte Carlo delta | −0.010 | 1.092 | −1.677 | 0.02 |

- All three hedges are **unbiased** (mean ≈ 0) once the premium is included.
- The **analytical barrier delta cuts the error standard deviation by about 28%** versus the naive vanilla delta and removes its strong skew.
- The **Monte Carlo delta** captures most of that improvement; the remaining gap comes from Monte Carlo noise in the delta (500 sub-paths per estimate).
- The remaining fat tails come from paths that cross the barrier between two rebalancing dates, where the delta jumps.

**Convergence** (analytical barrier delta, 5,000 paths):

| N | 25 | 100 | 400 |
|---|---|---|---|
| Std of hedging error | 1.87 | 0.95 | 0.50 |

Multiplying the rebalancing frequency by 4 halves the error, consistent with the `1/√N` rate of discrete delta hedging.

## Usage

```bash
git clone https://github.com/madiana93678/Barrier-Option-Pricing-MC.git
cd Barrier-Option-Pricing-MC
pip install -r requirements.txt
python main.py
```

Parameters (option type, knock-in/out, up/down, `S, K, B, T, r, sigma, N, M`) are set at the top of `main.py`.

## Project structure

```
├── main.py                 # Runs pricing and the three hedging strategies, prints metrics, plots errors
├── BarrierOption.py        # Simulation, payoff, Monte Carlo price, Reiner-Rubinstein closed form + BGK correction
├── DeltaHedger.py          # Hedging engine (premium, self-financing rebalancing) + analytical barrier delta
├── VanillaDeltaHedger.py   # Naive benchmark: Black-Scholes vanilla delta
├── MonteCarloHedger.py     # Monte Carlo bump-and-revalue delta with common random numbers
├── utils.py                # Hedging error metrics (mean, std, RMSE, quantile, skewness, kurtosis)
└── requirements.txt
```

## Possible extensions
- Transaction costs and hedging under a rebalancing band
- Gamma or vega hedging with a vanilla option, especially near the barrier
- Stochastic volatility (Heston) to measure model risk in the hedge
- Pathwise or likelihood-ratio Monte Carlo Greeks to reduce delta noise

## References
- Reiner, E. & Rubinstein, M. (1991). Breaking down the barriers. *Risk*, 4(8).
- Broadie, M., Glasserman, P. & Kou, S. (1997). A continuity correction for discrete barrier options. *Mathematical Finance*, 7(4).
- Glasserman, P. (2003). *Monte Carlo Methods in Financial Engineering*. Springer.
