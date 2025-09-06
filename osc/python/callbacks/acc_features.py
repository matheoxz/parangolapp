from signal_data.three_axis_buffer import ThreeAxisBuffer

"""
acc_features.py

Module containing accelerometer feature extraction functions.
Functions expect a ThreeAxisBuffer and return either
- tuple of per-axis metrics (x, y, z)
- or combined scalar metrics
"""
import numpy as np
from signal_data.three_axis_buffer import ThreeAxisBuffer

def _to_array(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Internal helper: convert ThreeAxisBuffer to (N,3) numpy array.
    """
    x, y, z = buffer.get()
    return np.column_stack((x, y, z))


def skewness(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute skewness of each axis in the buffer (tuple per axis).
    """
    arr = _to_array(buffer)
    m = np.mean(arr, axis=0)
    s = np.std(arr, axis=0)
    val = np.mean((arr - m)**3, axis=0) / (s**3 + 1e-8)
    return val


def kurtosis(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute excess kurtosis of each axis in the buffer (tuple per axis).
    """
    arr = _to_array(buffer)
    m = np.mean(arr, axis=0)
    s = np.std(arr, axis=0)
    val = np.mean((arr - m)**4, axis=0) / (s**4 + 1e-8) - 3
    return val


def energy(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute signal energy per axis (tuple per axis).
    """
    arr = _to_array(buffer)
    val = np.sum(arr**2, axis=0)
    return val


def mean(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute mean acceleration per axis (tuple per axis).
    """
    arr = _to_array(buffer)
    return np.mean(arr, axis=0)


def median(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute median acceleration per axis (tuple per axis).
    """
    arr = _to_array(buffer)
    return np.median(arr, axis=0)


def variance(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute variance per axis (tuple per axis).
    """
    arr = _to_array(buffer)
    return np.var(arr, axis=0)


def std(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute standard deviation per axis (tuple per axis).
    """
    arr = _to_array(buffer)
    return np.std(arr, axis=0)


def rms(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute root-mean-square amplitude per axis (tuple per axis).
    """
    arr = _to_array(buffer)
    return np.sqrt(np.mean(arr**2, axis=0))


def peak_to_peak(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute peak-to-peak range per axis (tuple per axis).
    """
    arr = _to_array(buffer)
    return np.ptp(arr, axis=0)


def sma(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute signal magnitude area per axis (tuple per axis).
    """
    arr = _to_array(buffer)
    return np.sum(np.abs(arr), axis=0)


def zero_crossing_rate(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute zero-crossing rate per axis (tuple of 3 values).
    """
    arr = _to_array(buffer)
    def zcr(a):
        s = np.sign(a)
        return ((s[:-1] * s[1:] < 0).sum() / (len(a)-1))
    return np.array([zcr(arr[:, i]) for i in range(3)])


def waveform_length(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute waveform length per axis (tuple of 3 values).
    """
    arr = _to_array(buffer)
    return np.array([np.sum(np.abs(np.diff(arr[:, i]))) for i in range(3)])


def iqr(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute interquartile range per axis (tuple of 3 values).
    """
    arr = _to_array(buffer)
    return np.array([np.percentile(arr[:, i], 75) - np.percentile(arr[:, i], 25) for i in range(3)])


def mad(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute median absolute deviation per axis (tuple of 3 values).
    """
    arr = _to_array(buffer)
    return np.array([np.median(np.abs(arr[:, i] - np.median(arr[:, i]))) for i in range(3)])


def crest_factor(buffer: ThreeAxisBuffer) -> np.ndarray:
    """
    Compute crest factor per axis (tuple of 3 values).
    """
    arr = _to_array(buffer)
    return np.array([np.max(np.abs(arr[:, i])) / (np.sqrt(np.mean(arr[:, i]**2)) + 1e-8) for i in range(3)])


def entropy(buffer: ThreeAxisBuffer, bins: int = 10) -> np.ndarray:
    """
    Compute Shannon entropy per axis (tuple of 3 values).
    """
    arr = _to_array(buffer)
    def ent(a):
        h,_ = np.histogram(a, bins=bins, density=True)
        h = h[h>0]
        return -np.sum(h*np.log2(h))
    return np.array([ent(arr[:, i]) for i in range(3)])


def covariance(buffer: np.ndarray) -> np.ndarray:
    """
    Compute covariance matrix (3x3) of axes over buffer.

    Interpretation:
    - Diagonal: variance per axis.
    - Off-diagonal: how two axes vary together.
    """
    return np.cov(buffer, rowvar=False)


def mobility_complexity(buffer: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute Hjorth mobility and complexity per axis.

    Interpretation:
    - Mobility: signal frequency content (higher → faster changes).
    - Complexity: variation of frequency (higher → more irregularity).
    """
    mobility = []
    complexity = []
    for i in range(buffer.shape[1]):
        x = buffer[:, i]
        dx = np.diff(x)
        ddx = np.diff(dx)
        varx = np.var(x)
        vardx = np.var(dx)
        varddx = np.var(ddx)
        m = np.sqrt(vardx / (varx + 1e-8))
        c = np.sqrt(varddx / (vardx + 1e-8)) / (m + 1e-8)
        mobility.append(m)
        complexity.append(c)
    return np.array(mobility), np.array(complexity)


def signal_vector_magnitude(buffer: np.ndarray) -> np.ndarray:
    """
    Compute signal vector magnitude per sample: sqrt(x^2 + y^2 + z^2).
    """
    return np.linalg.norm(buffer, axis=1)


def axis_correlation(buffer: np.ndarray) -> np.ndarray:
    """
    Compute Pearson correlation coefficients between axes:
    [corr(x,y), corr(x,z), corr(y,z)].
    """
    corr_mat = np.corrcoef(buffer, rowvar=False)
    return np.array([corr_mat[0,1], corr_mat[0,2], corr_mat[1,2]])


def cross_axis_energy_ratio(buffer: np.ndarray) -> np.ndarray:
    """
    Compute cross-axis energy ratios: [E_y/E_x, E_z/(E_x+E_y+E_z)].
    Uses sum(buffer^2) per axis as energy.
    """
    e = energy(buffer)
    total = e.sum() + 1e-8
    return np.array([e[1]/(e[0]+1e-8), e[2]/total])


def pca_explained_variance(buffer: np.ndarray) -> float:
    """
    Compute the explained variance ratio of the first principal component (3-axis data).
    Higher ratio => dominant motion direction.
    """
    data = buffer - np.mean(buffer, axis=0)
    cov = np.cov(data, rowvar=False)
    eigvals = np.linalg.eigvalsh(cov)
    total = eigvals.sum() + 1e-8
    # largest eigenvalue
    return np.max(eigvals) / total


def angular_change_stats(buffer: np.ndarray) -> np.ndarray:
    """
    Compute angles between consecutive acceleration vectors (degrees),
    then return [mean, variance, skewness, kurtosis] of that series.
    """
    mag = np.linalg.norm(buffer, axis=1)
    # avoid divide by zero
    normed = buffer / (mag[:, None] + 1e-8)
    dots = np.sum(normed[:-1] * normed[1:], axis=1)
    # clamp to [-1,1]
    dots = np.clip(dots, -1.0, 1.0)
    angles = np.degrees(np.arccos(dots))
    return np.array([
        np.mean(angles),
        np.var(angles),
        skewness(angles[:, None])[0],
        kurtosis(angles[:, None])[0]
    ])


def inter_axis_magnitude_ratios(buffer: np.ndarray) -> np.ndarray:
    """
    Compute inter-axis magnitude ratios:
    [max|x|/max|y|, mean|x|/mean(vector magnitude)].
    """
    max_abs = np.max(np.abs(buffer), axis=0)
    mag = signal_vector_magnitude(buffer)
    return np.array([
        max_abs[0] / (max_abs[1] + 1e-8),
        np.mean(np.abs(buffer[:,0])) / (np.mean(mag) + 1e-8)
    ])


def jerk_magnitude(buffer: np.ndarray, dt: float = 1.0) -> np.ndarray:
    """
    Compute jerk vector magnitude (rate of change of acceleration):
    magnitude of diff(buffer)/dt per sample (length N-1).
    """
    diff = np.diff(buffer, axis=0) / dt
    return np.linalg.norm(diff, axis=1)


def joint_entropy(buffer: np.ndarray, bins: int = 10) -> float:
    """
    Compute joint Shannon entropy of (x,y,z) via a 3D histogram.
    Higher entropy indicates more uniformly distributed multi-axis motion.
    """
    hist, _ = np.histogramdd(buffer, bins=bins, density=True)
    p = hist.flatten()
    p = p[p > 0]
    return -np.sum(p * np.log2(p))


def svm_stats(buffer: np.ndarray) -> dict:
    """
    Compute basic stats on signal vector magnitude:
    mean, rms, variance, peak-to-peak, skewness, kurtosis, entropy.
    Returns a dict with keys 'mean','rms','var','ptp','skew','kurt','entropy'.
    """
    svm = signal_vector_magnitude(buffer)
    return {
        'mean': np.mean(svm),
        'rms': np.sqrt(np.mean(svm**2)),
        'var': np.var(svm),
        'ptp': np.ptp(svm),
        'skew': skewness(svm[:, None])[0],
        'kurt': kurtosis(svm[:, None])[0],
        'entropy': entropy(svm[:, None])[0]
    }