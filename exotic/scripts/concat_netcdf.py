import sys
import subprocess
import os

import yaml
import xarray as xr

DIRNAME = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(DIRNAME, '../config.yaml')


def main():
    forcing = sys.argv[1]
    first_netcdf = int(sys.argv[2])
    last_netcdf = int(sys.argv[3])

    # Read configuration file
    try:
        with open(CONFIG_PATH) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError:
        print('config.yaml not found')

    data_path = config['data_path']

    print('listing files')
    # cmd = f"ls {os.path.join(data_path, netcdf_dir, f'sim*{{{first_netcdf.zfill(6)}..{last_netcdf.zfill(6)}}}.nc')}"
    # print('executing command')
    # cmd_output = subprocess.check_output(cmd, shell=True, executable='/bin/bash')
    # print('decoding output')
    # nc_to_concat = cmd_output.decode("utf-8").split('\n')[:-1]
    nc_to_concat = [
        os.path.join(
            data_path,
            forcing,
            f'sim_lorenz96_rk4_{forcing}_all_{str(i).zfill(6)}.nc')
        for i in range(first_netcdf, last_netcdf + 1)
    ]

    print('opening')
    ds = xr.open_mfdataset(
        nc_to_concat,
        combine='nested',
        concat_dim='realization',
        chunks={'time_step': 100},
        # parallel=True
    )

    out_name = f"merged_{str(first_netcdf).zfill(6)}_{str(last_netcdf).zfill(6)}.nc"

    print('saving')
    ds.to_netcdf(
        os.path.join(data_path, forcing, out_name),
        encoding={'var': {'zlib': True, 'complevel': 9}}
    )


if __name__ == "__main__":
    main()
