import xarray as xr
import typing as T


class Energy:

    def __call__(
            self,
            data: xr.DataArray
    ):

        obs = 0.5*(data**2)

        return obs

    @property
    def short_name(self):

        return 'energy'


class Bin:

    def __init__(
            self,
            data: xr.DataArray,
            threshold: T.Union[T.List[float, ], T.List[float, float]]
    ):

        if len(threshold) == 1:
            obs = data.where(data > threshold[0], 0)
            obs = obs.where(obs == 0, 1)
        else:
            obs = data.where(threshold[0] < data < threshold[1], 0)
            obs = obs.where(obs == 0, 1)

        return obs

    @property
    def short_name(self):

        if len(threshold) == 1:
            return 'exceed_{}'.format(round(threshold[0], 1))
        else:
            return 'bin_{}_{}'.format(round(threshold[0], 1), round(threshold[1], 1))
