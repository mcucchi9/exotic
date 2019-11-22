import sys
import subprocess
import os

import yaml
import xarray as xr

DIRNAME = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(DIRNAME, '../config.yaml')


def main():
    netcdf_dir = sys.argv[1]
    first_netcdf = sys.argv[2]
    last_netcdf = sys.argv[3]

    # Read configuration file
    try:
        with open(CONFIG_PATH) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError:
        print('config.yaml not found')

    data_path = '/home/cucchi/phd/data/sim/lorenz96/rk4/t_1_00/'

    cmd = f"ls {os.path.join(data_path, netcdf_dir, f'sim*{{{first_netcdf.zfill(6)}..{last_netcdf.zfill(6)}}}.nc')}"
    cmd_output = subprocess.check_output(cmd, shell=True, executable='/bin/bash')
    nc_to_concat = cmd_output.decode("utf-8").split('\n')[:-1]

    ds = xr.open_mfdataset(
        nc_to_concat,
        combine='nested',
        concat_dim='realization'
    )

    out_name = f"merged_{first_netcdf.zfill(6)}_{last_netcdf.zfill(6)}.nc"
    
    ds.to_netcdf(
        os.path.join(data_path, netcdf_dir, out_name),
        encoding={'var': {'zlib': True, 'complevel': 9}}
    )


if __name__ == "__main__":
    main()
