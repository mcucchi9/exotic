import xarray as xr
import typing as T
import numpy as np


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


class Position:

    def __call__(
            self,
            data: xr.DataArray
    ):

        obs = data

        return obs

    @property
    def short_name(self):

        return 'position'


class Bin:

    def __init__(
            self,
            threshold: T.List[float],
            threshold_q: T.List[float],
            observable
    ):

        self.threshold = threshold
        self.threshold_q = threshold_q
        self.observable = observable

    def __call__(
            self,
            data=xr.DataArray
    ):

        data = self.observable(data)
        ones = xr.ones_like(data)

        if len(self.threshold) == 1:
            obs = ones.where(data > self.threshold[0], 0)
        else:
            obs1 = ones.where(data > self.threshold[0], 0)
            obs2 = ones.where(data <= self.threshold[1], 0)

            obs = obs1 * obs2

        return obs

    @property
    def short_name(self):

        if len(self.threshold) == 1:
            return '{}_exceed_{}q'.format(self.observable.short_name, np.round(self.threshold_q[0], 3))
        else:
            return '{}_bin_{}q_{}q'.format(
                self.observable.short_name,
                np.round(self.threshold_q[0], 3),
                np.round(self.threshold_q[1], 3)
            )
