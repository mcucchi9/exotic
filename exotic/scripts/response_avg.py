import sys
import os
import xarray as xr
import numpy as np
from slack_progress import SlackProgress
from slackclient import SlackClient

sys.path.append('../devel/phd/')

from lab.simulation import observables

DATA_PATH = os.environ.get('BASE_DATA_PATH')

OBS_DICT = {
    'energy': observables.Energy,
    'position': observables.Position,
    'bin': observables.Bin,
    'below': observables.Below
}

forcing_sn = sys.argv[1]
obs_sn = sys.argv[2]

obs_main = obs_sn.split('_')[0]
obs_stat = obs_sn.split('_')[1]

if obs_stat in ('bin', 'below'):

    threshold_q = []
    threshold_q.append(round(float(sys.argv[3]), 2))
    try:
        threshold_q.append(round(float(sys.argv[4]), 2))
    except:
        print('only one threshold selected')

    quantiles = xr.open_dataarray(os.path.join(
        DATA_PATH,
        'obs/lorenz96/rk4/CF_8/quantiles/obs_lorenz96_rk4_CF_8_quantiles_{}.nc'.format(obs_main))
    )
    quantile_orders = np.round(quantiles.quantile_order.values, 2)
    quantiles.quantile_order.values = quantile_orders
    threshold = [quantiles.sel(quantile_order=tq).values for tq in threshold_q]

observable_class = OBS_DICT[obs_stat]
if obs_stat in ('bin', 'below'):
    observable = observable_class(threshold, threshold_q, OBS_DICT[obs_main]())
else:
    observable = observable_class()

data_noforcing_path = os.path.join(
    DATA_PATH,
    'sim/lorenz96/rk4/CF_8/'
)
data_forcing_path = os.path.join(
    DATA_PATH,
    'sim/lorenz96/rk4/{}/'.format(forcing_sn)
)

num_forcing_sim = len(os.listdir(data_forcing_path))

counter = 0
for i in range(1, num_forcing_sim):
    # compute observation forcing
    file_name_forcing = 'sim_lorenz96_rk4_{}_one_{:05}.nc'.format(forcing_sn, i)
    data_forcing = xr.open_dataarray(os.path.join(data_forcing_path, file_name_forcing))
    obs_forcing = observable(data_forcing)
    obs_forcing.attrs = data_forcing.attrs
    # compute observation no forcing
    file_name_noforcing = 'sim_lorenz96_rk4_CF_8_one_{:05}.nc'.format(i)
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

response_avg.attrs['forcing'] = forcing_sn
response_avg.attrs['observable'] = observable.short_name
response_avg.attrs['ensemble'] = num_forcing_sim - 1

# Save Average Response

out_name = os.path.join(
    DATA_PATH,
    'response/lorenz96/rk4/{}/{}/{}'.format(forcing_sn, obs_main, obs_stat),
    'response_lorenz96_rk4_{}_{}.nc'.format(observable.short_name, forcing_sn)
)

if not os.path.exists(os.path.dirname(out_name)):
    os.makedirs(os.path.dirname(out_name))

response_avg.to_netcdf(out_name)

