import os
from sim import simulation as sim
import numpy as np
# import xarray as xr
from netCDF4 import Dataset

point = sim.SystemState([1, 2, 3, 4, 5, 6], 0)
traj = sim.Simulator(system_state=point)

integration_time = 10
integration_steps = int(integration_time/traj.increment)
chunk_steps = 100
chunks = int(integration_steps/chunk_steps)

file_path = '/home/cucchi/phd/prova.nc'

if os.path.exists(file_path):
    os.remove(file_path)

dataset = Dataset(file_path, 'w')

lon = dataset.createDimension('node', len(point.coords))
time = dataset.createDimension('time', None)

times = dataset.createVariable('time', np.float64, ('time',))
nodes = dataset.createVariable('node', np.int32, ('node',))

var = dataset.createVariable('var', np.float32, ('time', 'node'))

dim = len(point.coords)

for chunk in np.arange(0, chunks):
    # initialize chunk numpy array
    print(chunk)
    t = []
    data_array = np.empty((chunk_steps, dim))
    for i in np.arange(0, chunk_steps):
        data_array[i, :] = point.coords
        t.append(point.time)
        traj.integrate()
    # data_array = xr.DataArray(data_nparray, dims=('time', 'node'), coords={'time': t, 'node': [0, 1, 2, 3, 4, 5]})
    # data_set = data_array.to_dataset(name='var')
    # data_array = xr.DataArray(data_nparray)
    # print(data_set)
    # data_set.to_netcdf('/home/cucchi/phd/prova.nc', mode='a', unlimited_dims='time')
