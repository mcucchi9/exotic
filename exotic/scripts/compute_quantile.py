import sys
import os
import xarray as xr
import numpy as np
from slack_progress import SlackProgress
from slackclient import SlackClient

sys.path.append('/home/users/tx827782/devel/phd')
DATA_PATH = os.environ.get('BASE_DATA_PATH')

from lab.simulation import observables

OBS_DICT = {
   'energy': observables.Energy,
   'position': observables.Position
}

# instantiate Slack client
sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
sp = SlackProgress(os.environ.get('SLACK_BOT_TOKEN'), '#l96lrt')

obs = sys.argv[1]
q_start = float(sys.argv[2])
q_stop = float(sys.argv[3])
q_step = float(sys.argv[4])

obs_class = OBS_DICT[obs]

quantile_orders = [q for q in np.arange(q_start, q_stop, q_step)]
sim_num = 1000

sc.api_call(
    "chat.postMessage",
    channel="#l96lrt",
    text="Computing {} Quantiles, from {} to {} by {}".format(obs, q_start, q_stop, q_step)
)

sc.api_call(
    "chat.postMessage",
    channel="#l96lrt",
    text="Importing files"
)
pbar = sp.new(total=100)

counter = 0

for i in np.arange(1, sim_num + 1):

    file_path = os.path.join(
        DATA_PATH,
        'sim/lorenz96/rk4/CF_8',
        'sim_lorenz96_rk4_CF_8_one_{:05}.nc'.format(i)
    )

    data = xr.open_dataarray(file_path)
    observable = obs_class()

    observable_values = observable(data)

    if counter == 0:
        observable_values_arr = observable_values.values.squeeze()
    else:
        observable_values_arr = np.concatenate((observable_values_arr, observable_values.values.squeeze()))

    counter += 1

    if counter%10 == 0:
        try:
            pbar.pos = round(counter / (sim_num) * 100)
        except:
            pass

sc.api_call(
    "chat.postMessage",
    channel="#l96lrt",
    text="Computing quantiles"
)
pbar = sp.new(total=100)

quantiles = []
counter = 0

for q in quantile_orders:

    quantile = np.quantile(observable_values_arr, q)
    quantiles.append(quantile)

    counter += 1

    try:
        pbar.pos = round(counter / (len(quantile_orders)) * 100)
    except:
        pass

quantiles_dataarray = xr.DataArray(quantiles, coords=[quantile_orders], dims=['quantile_order'])

out_path = os.path.join(
    DATA_PATH,
    'obs/lorenz96/rk4/CF_8/quantiles/obs_lorenz96_rk4_CF_8_quantiles_{}.nc'.format(obs)
)

out_path_new = os.path.join(
    DATA_PATH,
    'obs/lorenz96/rk4/CF_8/quantiles/obs_lorenz96_rk4_CF_8_quantiles_{}_new.nc'.format(obs)
)


if not os.path.exists(os.path.dirname(out_path)):
    os.makedirs(os.path.dirname(out_path))

try:
    quantiles_dataarray_old = xr.open_dataarray(out_path)
    quantiles_dataarray_new = xr.concat([quantiles_dataarray_old, quantiles_datarray], dim='quantile_order')
    # quantiles_dataarray_new.attrs['total_timesteps'] = sim_num * 10000
    quantiles_dataarray_new.to_netcdf(out_path_new)
except:
    quantiles_dataarray.attrs['total_timesteps'] = sim_num * 10000
    quantiles_dataarray.to_netcdf(out_path_new)
