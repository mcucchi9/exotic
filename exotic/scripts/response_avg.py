import sys
import os
import glob
import xarray as xr
import numpy as np
from slack_progress import SlackProgress
from slackclient import SlackClient

sys.path.append('../')

from lab.simulation import observables

dirname = os.path.dirname(__file__)
DATA_PATH = os.path.join(dirname, '../../../../data')

OBS_DICT = {
    'energy': observables.Energy,
    'position': observables.Position,
    'bin': observables.Bin,
    'below': observables.Below,
    'exceed': observables.Exceed
}

forcing_sn = sys.argv[1]
obs_sn = sys.argv[2]

# this is the actual observable (e.g. energy, position)
obs_main = obs_sn.split('_')[0]
# this is the statistics (e.g. freq of values below a certain threshold)
obs_stat = obs_sn.split('_')[1]

if obs_stat in ('bin', 'below', 'exceed'):

    threshold_q = list()
    threshold_q.append(round(float(sys.argv[3]), 2))
    try:
        threshold_q.append(round(float(sys.argv[4]), 2))
    except:
        print('only one threshold selected')

    quantiles = xr.open_dataarray(os.path.join(
        DATA_PATH,
        f'obs/lorenz96/rk4/CF_8.0/quantiles/obs_lorenz96_rk4_CF_8.0_quantiles_{obs_main}.nc')
    )
    quantiles_orders = np.round(quantiles.quantile_order.values, 2)
    quantiles.assign_coords(coords={'quantile_order': quantiles_orders})
    threshold = [quantiles.sel(quantile_order=tq).values for tq in threshold_q]

observable_class = OBS_DICT[obs_stat]
if obs_stat in ('bin', 'below', 'exceed'):
    observable = observable_class(threshold, threshold_q, OBS_DICT[obs_main]())
else:
    observable = observable_class()

data_noforcing_path = os.path.join(
    DATA_PATH,
    'sim/lorenz96/rk4/CF_8.0/'
)
data_forcing_path = os.path.join(
    DATA_PATH,
    f'sim/lorenz96/rk4/{forcing_sn}/'
)

num_forcing_sim = len(glob.glob(f'{data_forcing_path}/*tbr0.01*'))

# TODO: make tbr0.01 a user input
counter = 0
# NOTE: I ignore the 00000 simulation (not yet on attractor)
for i in range(1, num_forcing_sim):
    # compute observation forcing
    file_name_forcing = f'sim_lorenz96_rk4_{forcing_sn}_tbr0.01_one_{i:05}.nc'
    data_forcing = xr.open_dataarray(os.path.join(data_forcing_path, file_name_forcing))
    obs_forcing = observable(data_forcing)
    obs_forcing.attrs = data_forcing.attrs
    # compute observation no forcing
    file_name_noforcing = f'sim_lorenz96_rk4_CF_8.0_tbr0.01_one_{i:05}.nc'
    data_noforcing = xr.open_dataarray(os.path.join(data_noforcing_path, file_name_noforcing))
    obs_noforcing = observable(data_noforcing)
    obs_noforcing.attrs = data_noforcing.attrs
    # compute response
    response = obs_forcing - obs_noforcing
    if counter == 0:
        response_avg = response
    else:
        response_avg += response  
    counter += 1

response_avg = response_avg/counter

response_avg['var'].attrs['forcing'] = forcing_sn
response_avg['var'].attrs['observable'] = observable.short_name
response_avg['var'].attrs['ensemble'] = num_forcing_sim - 1

# Save Average Response

out_name = os.path.join(
    DATA_PATH,
    f'response/lorenz96/rk4/{forcing_sn}/{obs_main}/'
    f'response_lorenz96_rk4_{observable.short_name}_{forcing_sn}.nc'
)

if not os.path.exists(os.path.dirname(out_name)):
    os.makedirs(os.path.dirname(out_name))

response_avg.to_netcdf(out_name)

