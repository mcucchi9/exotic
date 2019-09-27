import sys
import os
import xarray as xr
from slackclient import SlackClient
from slack_progress import SlackProgress

sys.path.append('../')

import lab.simulation.simulation as sim
import lab.simulation.forcings as forcings
import lab.simulation.systems as systems
import lab.simulation.integrators as integrators

# instantiate Slack client
sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
sp = SlackProgress(os.environ.get('SLACK_BOT_TOKEN'), '#l96lrt')

DATA_PATH = os.environ.get('BASE_DATA_PATH')

initial_conditions = xr.open_dataarray(os.path.join(
    DATA_PATH,
    'sim/lorenz96/rk4/t_1_00/CF_8.0/sim_lorenz96_rk4_CF_8.0_all_init.nc'
))

system = systems.Lorenz96()
int_method = integrators.RungeKutta4()

forcing_id = (sys.argv[1])

sim_start = int(sys.argv[2])
sim_num = int(sys.argv[3])
take_init_every_steps = int(sys.argv[4])

if forcing_id == 'constant':
    force = forcings.ConstantForcing(
        force_intensity=float(sys.argv[5])
    )
elif forcing_id == 'delta':
    force = forcings.DeltaForcing(
        activation_time=0,
        force_intensity_base=float(sys.argv[5]),
        force_intensity_delta=float(sys.argv[6])
    )
elif forcing_id == 'step':
    force = forcings.DeltaForcing(
        activation_time=0,
        force_intensity_base=float(sys.argv[5]),
        force_intensity_delta=float(sys.argv[6])
    )
elif forcing_id == 'linear':
    force = forcings.LinearForcing(
        activation_time=0,
        deactivation_time=0,
        force_intensity_base=float(sys.argv[5]),
        linear_coefficient=float(sys.argv[6])
    )
elif forcing_id == 'sinusoidal':
    force = forcings.SinusoidalForcing(
        activation_time=0,
        deactivation_time=0,
        force_intensity_base=float(sys.argv[5]),
        epsilon=float(sys.argv[6]),
        omega=float(sys.argv[7])
    )
else:
    raise ValueError('{} forcing not supported!'.format(forcing_id))

sc.api_call(
    "chat.postMessage",
    channel="#l96lrt",
    text="Running {} simulations with forcing CF_{}_0".format(sim_num, force_intensity)
)

pbar = sp.new()

for sim_index in range(sim_start, sim_start + sim_num):

    time_step_real = int(sim_index*take_init_every_steps/initial_conditions.integration_step)

    point = sim.SystemState(
        coords=initial_conditions.sel(time_step=time_step_real).values,
    )

    simulator = sim.Simulator(
        system_state=point,
        forcing=force,
        int_method=int_method,
        system=system
    )

    runner = sim.SimulationRunner(
        simulator=simulator,
        integration_time=100,
        chunk_length_time=1000,
        write_all_every=1,
        write_one_every=0
    )

    outfiles = runner.run(
        data_base_path=DATA_PATH,
        custom_suffix='{:06}'.format(sim_index),
        custom_attrs={'time_step_0_real': time_step_real}
    )

    try:
        pbar.pos = round((sim_index-sim_start)/sim_num*100)
    except:
        pass

