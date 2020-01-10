import sys
import subprocess
import os

import yaml
import xarray as xr

DIRNAME = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(DIRNAME, '../config.yaml')


def generate_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def main():
    forcing = sys.argv[1]
    first_netcdf = int(sys.argv[2])
    last_netcdf = int(sys.argv[3])
    group_size = int(sys.argv[4])

    # Read configuration file
    try:
        with open(CONFIG_PATH) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError:
        print('config.yaml not found')

    data_path = config.get('data_path', None)

    all_files = os.listdir(os.path.join(data_path, forcing))

    print('listing files')
    nc_to_concat_all = [
        os.path.join(
            data_path,
            forcing,
            f'sim_lorenz96_rk4_{forcing}_all_{str(i).zfill(6)}.nc')
        for i in range(first_netcdf, last_netcdf + 1)
    ]

    files_to_concat_number = len(nc_to_concat_all)

    iteration = 0

    while files_to_concat_number > group_size:

        nc_to_concat_all_grp = list(generate_chunks(nc_to_concat_all, group_size))
        groups_number = len(nc_to_concat_all_grp)
        tmp_out_path_all = []
        
        if iteration==0:
            chunks_dict = {'time_step': 100, 'node': 32}
        else:
            chunks_dict = {'time_step': 100, 'node': 32, 'realization': 100}

        for i in range(0, groups_number):

            nc_to_concat = nc_to_concat_all_grp[i]

            tmp_out_name = f"tmp_{iteration}_{i}_{groups_number}.nc"
            tmp_out_path = os.path.join(data_path, forcing, tmp_out_name)

            if tmp_out_name not in all_files:

                print(f"iteration {iteration}, opening group {i}/{groups_number}")
                ds = xr.open_mfdataset(
                    nc_to_concat,
                    combine='nested',
                    concat_dim='realization',
                    chunks=chunks_dict
                    # parallel=True
                )
                
                if iteration == 0:
                    ds = ds.assign_coords({'realization': list(range(i*group_size, i*group_size+len(nc_to_concat)))})   

                print(f"saving to {tmp_out_name}")
                ds.to_netcdf(
                    tmp_out_path,
                    encoding={'var': {'zlib': True, 'complevel': 9}}
                )

            tmp_out_path_all.append(tmp_out_path)

        files_to_concat_number = len(tmp_out_path_all)
        nc_to_concat_all = tmp_out_path_all

        iteration = iteration + 1

    out_name = f"merged_{str(first_netcdf).zfill(6)}_{str(last_netcdf).zfill(6)}.nc"

    print("opening tmp files")
    ds = xr.open_mfdataset(
        nc_to_concat_all,
        combine='nested',
        concat_dim='realization',
        chunks=chunks_dict,
        # parallel=True
    )

    print('saving final')
    ds.to_netcdf(
        os.path.join(data_path, forcing, out_name),
        encoding={'var': {'zlib': True, 'complevel': 9}}
    )


if __name__ == "__main__":
    main()
