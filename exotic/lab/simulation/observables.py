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
            data: xr.DataArray
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

        return f'{self.observable.short_name}_bin' \
               f'_{np.round(self.threshold_q[0], 3):02}q' \
               f'_{np.round(self.threshold_q[1], 3):02}q'


class Below:

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
            data: xr.DataArray
    ):

        data = self.observable(data)
        ones = xr.ones_like(data)

        obs = ones.where(data < self.threshold[0], 0)

        return obs

    @property
    def short_name(self):

        return f'{self.observable.short_name}_below_{np.round(self.threshold_q[0], 3):02}q'


class Exceed:

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
            data: xr.DataArray
    ):

        data = self.observable(data)
        ones = xr.ones_like(data)

        obs = ones.where(data > self.threshold[0], 0)

        return obs

    @property
    def short_name(self):

        return f'{self.observable.short_name}_exceed_{np.round(self.threshold_q[0], 3):02}q'
