import numpy as np
import xarray as xr
from sim import simulation as sim

point = sim.SystemState(coords=[1, 2, 3, 4, 5])
traj = sim.Simulator(system_state=point)

times = [0]

a = point.coords


for k in np.arange(0, 1000, 0.01):
    times.append(k)
    traj.integrate()
    a = np.vstack((a, point.coords))

data = xr.DataArray(a,
                    coords=[times, [1, 2, 3, 4, 5]],
                    dims=['time', 'node'])

data.to_netcdf('/home/cucchi/phd/prova.nc')

pd_data = data.to_pandas()

pd_data.to_csv('/home/cucchi/phd/prova.csv')

pd_data.columns = pd_data.columns.astype(str)

pd_data.reset_index().to_feather('/home/cucchi/phd/prova.feather')

