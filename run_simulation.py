import os
from sim import simulation as sim
import numpy as np
import xarray as xr
from netCDF4 import Dataset

point = sim.SystemState([1,2,3,4,5,6], 0)
traj = sim.Simulator(system_state=point)

integration_time = 10
integration_steps = int(integration_time/traj.increment)
chunk_steps = 100
chunks = int(integration_steps/chunk_steps)

file_path = '/home/cucchi/phd/prova.nc'

if os.path.exists(file_path):
    os.remove(file_path)

Dataset(file_path, 'w')

dim = len(point.coords)

for chunk in np.arange(0, chunks):
    # initialize chunk numpy array
    print(chunk)
    t = []
    data_nparray = np.empty((chunk_steps, dim))
    for i in np.arange(0, chunk_steps):
        data_nparray[i,:] = point.coords
        t.append(point.time)
        traj.integrate()
    data_array = xr.DataArray(data_nparray, dims=('time', 'node'), coords={'time': t, 'node': [0, 1, 2, 3, 4, 5]})
    #data_array = xr.DataArray(data_nparray)
    print(data_array)
    data_array.to_netcdf('/home/cucchi/phd/prova.nc', mode='a')
