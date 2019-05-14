import numpy as np
import math


def compute_susceptibility(
        series: np.ndarray
) -> np.ndarray:
    """
    Compute susceptiility chi if series is response to unit step forcing
    :param series: response to unit step forcing
    :return:
    """

    green_function = np.diff(series)

    nt = len(series)
    nfft = 2 ** (math.ceil(math.log2(abs(nt))))

    green_function_extd = np.zeros(2 * nfft)
    green_function_extd[0:len(green_function)] = green_function
    green_function_extd = np.roll(green_function_extd, nfft)

    chi = np.fft.fft(green_function_extd)

    return chi


def compute_response(
        chi: np.ndarray,
        forcing
) -> np.ndarray:
    """
    Compute response to **forcing** given extended susceptibility **chi**
    :param chi: extended susceptibility
    :param forcing: forcing function (from lab.forcings)
    :return:
    """
    nfft = int(len(chi)/2)
    f = [forcing(t*0.01) - 8 for t in np.arange(0, nfft)]

    f_extd = np.zeros(2 * nfft)
    f_extd[nfft:(nfft + len(f))] = f

    F_extd = np.fft.fft(f_extd)

    resp = np.fft.ifft(chi * (F_extd))

    return np.real(resp)