import sys
import os
import xarray as xr
from slackclient import SlackClient
from slack_progress import SlackProgress

sys.path.append('../devel/phd')

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
    'sim/lorenz96/rk4/CF_8/sim_lorenz96_rk4_CF_8_all_00000.nc'
))

system = systems.Lorenz96()
int_method = integrators.RungeKutta4()
epsilon = float(sys.argv[1])
omega = float(sys.argv[2])
deactivation_time = int(sys.argv[3])
sim_num = int(sys.argv[4])

forcing_str = 'SinF_8_{}_{}_0_{}'.format(epsilon, omega, deactivation_time)

sc.api_call(
    "chat.postMessage",
    channel="#l96lrt",
    text="Running {} simulations with forcing {}".format(sim_num, forcing_str)
)

pbar = sp.new()

for i in range(0, sim_num):

    #check if output file already exists and, in case, skip

    outfile = os.path.join(
        DATA_PATH,
        'sim/lorenz96/rk4/{force}/sim_lorenz96_rk4_{force}_{index:05}.nc'.format(force=forcing_str, index=i)
    )

    if not os.path.isfile(outfile):

        time_step_real = int(i*100/initial_conditions.integration_step)

        point = sim.SystemState(
            coords=initial_conditions.sel(time_step=time_step_real).values,
        )

        force = forcings.SinusoidalForcing(
	    epsilon=epsilon,
            omega=omega,
	    deactivation_time = deactivation_time
        )

        simulator = sim.Simulator(
            system_state=point,
            forcing=force,
            int_method=int_method,
            system=system
        )

        runner = sim.SimulationRunner(
           simulator=simulator,
        )

        outfiles = runner.run(
           integration_time=100,
           chunk_length=10000,
           write_all_every=0,
           data_base_path=DATA_PATH,
           custom_suffix='{:05}'.format(i),
           custom_attrs={'time_step_0_real': time_step_real}
        )
 
    try:
        pbar.pos = round(i/sim_num*100)
    except:
        pass
	

