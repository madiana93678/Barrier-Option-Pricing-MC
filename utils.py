import numpy as np
from scipy.stats import skew, kurtosis

def compute_metrics(hedging_errors):
    """
    Compute important metrics for evaluating the hedging performance.
    
    Parameters:
        hedging_errors (np.ndarray): Array of hedging errors for all paths (M).
    
    Returns:
        dict: Dictionary containing various performance metrics.
    """
    # Mean hedging error
    mean_error = np.mean(hedging_errors)

    # Standard deviation of hedging error
    std_error = np.std(hedging_errors)

    # Maximum hedging error
    max_error = np.max(hedging_errors)

    # Minimum hedging error
    min_error = np.min(hedging_errors)

    # Skewness
    error_skewness = skew(hedging_errors)

    # Kurtosis
    error_kurtosis = kurtosis(hedging_errors)

    # Print metrics
    print(f"Mean Hedging Error: {mean_error:.4f}")
    print(f"Standard Deviation of Hedging Error: {std_error:.4f}")
    print(f"Maximum Hedging Error: {max_error:.4f}")
    print(f"Minimum Hedging Error: {min_error:.4f}")
    print(f"Skewness of Hedging Error: {error_skewness:.4f}")
    print(f"Kurtosis of Hedging Error: {error_kurtosis:.4f}")

    # Return metrics as a dictionary
    return {
        "Mean Hedging Error": mean_error,
        "Standard Deviation": std_error,
        "Max Hedging Error": max_error,
        "Min Hedging Error": min_error,
        "Skewness": error_skewness,
        "Kurtosis": error_kurtosis
    }