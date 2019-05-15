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
            threshold: T.List[float],
            observable
    ):

        self.threshold = threshold
        self.observable = observable

    def __call__(
            self,
            data=xr.DataArray
    ):

        data = self.observable(data)

        if len(self.threshold) == 1:
            obs = data.where(data > self.threshold[0], 0)
            obs = obs.where(obs == 0, 1)
        else:
            obs = data.where(self.threshold[0] < data < self.threshold[1], 0)
            obs = obs.where(obs == 0, 1)

        return obs

    @property
    def short_name(self):

        if len(self.threshold) == 1:
            return '{}_exceed_{}'.format(self.observable.short_name, round(self.threshold[0], 1))
        else:
            return '{}_bin_{}_{}'.format(
                self.observable.short_name,
                round(self.threshold[0], 1),
                round(self.threshold[1], 1)
            )
