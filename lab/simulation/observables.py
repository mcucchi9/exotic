import xarray as xr


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
