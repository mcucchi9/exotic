import numpy as np
import math


def compute_green_function(
        series: np.ndarray
) -> np.ndarray:

    nt = len(series)
    nfft = 2 ** (math.ceil(math.log2(abs(nt))))
    series_extd = np.zeros(2 * nfft)
    series_extd[0:len(series)] = series
    series_extd = np.roll(series_extd, nfft)

    chi = np.fft.fft(series_extd)

    return chi