import numpy as np
from scipy.stats import skew, kurtosis


def compute_metrics(hedging_errors, label=None, verbose=True):
    """
    Summary statistics of the hedging errors.

    Parameters:
        hedging_errors (np.ndarray): Hedging error on each path.
        label (str): Optional name printed before the metrics.
        verbose (bool): Print the metrics.

    Returns:
        dict: Mean, standard deviation, RMSE, min, max, 5% quantile, skewness, excess kurtosis.
    """
    e = np.asarray(hedging_errors)
    metrics = {
        "Mean": np.mean(e),
        "Std": np.std(e, ddof=1),
        "RMSE": np.sqrt(np.mean(e ** 2)),
        "Min": np.min(e),
        "Max": np.max(e),
        "5% quantile": np.quantile(e, 0.05),
        "Skewness": skew(e),
        "Excess kurtosis": kurtosis(e),
    }
    if verbose:
        if label:
            print(f"\n{label}")
        for k, v in metrics.items():
            print(f"  {k:<16}{v: .4f}")
    return metrics
