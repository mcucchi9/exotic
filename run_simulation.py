import sys

import lab.simulation.simulation as sim
import lab.simulation.forcings as forcings
import lab.simulation.systems as systems
import lab.simulation.integrators as integrators

sys.path.append('../')

DATA_PATH = '../data/'

point_const = sim.SystemState(coords=[8]*32)
point_const.perturbate()
constant_force = forcings.ConstantForcing()
system = systems.Lorenz96()
int_method = integrators.RungeKutta4()

simulator_const = sim.Simulator(
    system_state=point_const,
    forcing=constant_force,
    int_method=int_method,
    system=system
)

runner = sim.SimulationRunner(
    simulator=simulator_const,
)

runner.run(
    integration_time=100,
    chunk_length=10000,
    write_all_every=1000,
    data_base_path=DATA_PATH
)

