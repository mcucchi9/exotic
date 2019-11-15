import sys
import os

import yaml
import xarray as xr

netcdf_dir = sys.argv[1]

DIRNAME = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(DIRNAME, '../config.yaml')

# Read configuration file
try:
    with open(CONFIG_PATH) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
except FileNotFoundError:
    print('config.yaml not found')

data_path = '/home/cucchi/phd/data/sim/lorenz96/rk4/t_1_00/'

print(os.path.join(data_path, netcdf_dir, f'*{{{first_netcdf.zfill(6)}..{last_netcdf.zfill(6)}}}.nc'))

ds = xr.open_mfdataset(
    #os.path.join(data_path, netcdf_dir, f'*{{{first_netcdf.zfill(6)}..{last_netcdf.zfill(6)}}}.nc'),
    os.path.join(data_path, netcdf_dir, f'*.nc'),
    combine='nested',
    concat_dim='realization'
)

ds.to_netcdf(
    os.path.join(data_path, netcdf_dir, 'merged.nc')
)
