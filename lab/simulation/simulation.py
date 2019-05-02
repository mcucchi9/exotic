import numpy as np
import netCDF4 as nc
import os

from . import forcings
from . import integrators


#TODO: REMOVE
def runge_kutta_4(x: list, f: float, fx, hs: float):
    """
    This method implement 4th order Runge-Kutta integration method.
    :param x: coordinates at time t0
    :param f: external forcing
    :param fx: first-order differential equations system.
    :param hs: time increment (dt)
    :return: coordinates at time t1 = t0 + hs
    """
    k1 = fx(x, f) * hs
    xk = x + k1 * 0.5
    k2 = fx(xk, f) * hs
    xk = x + k2 * 0.5
    k3 = fx(xk, f) * hs
    xk = x + k3
    k4 = fx(xk, f) * hs

    x = x + (k1 + 2 * (k2 + k3) + k4) / 6

    return x


#TODO: REMOVE
def lorenz_96(x, forcing):
    """
    This method implement Lorenz-96 first-order differential equations system.
    :param x: coordinates at time t0
    :param forcing: (constant) forcing term
    :return: state derivatives at time t0
    """
    n = len(x)

    d = np.zeros(n)

    for i in range(0, n):
        d[i] = (x[(i+1) % n] - x[i-2]) * x[i-1] - x[i] + forcing

    return d


class SystemState:

    def __init__(self, coords=(0, 0, 0), time=0):
        """

        :param coords: coordinates
        :param time: time
        """
        self.coords = coords
        self.time = time

    def __repr__(self):
        return "coordinates: {}\n" \
               "time: {}".format(self.coords, self.time)

    @property
    def energy(self):
        return np.sum(0.5*(np.square(self.coords)))

    def perturbate(self, intensity=0.05):

        random_seed = 1234

        np.random.seed(random_seed)
        perturbation = np.random.uniform(-intensity, intensity, size=len(self.coords))

        self.coords += perturbation


class Simulator:
    """
    Integrate point and system information, include functionality to integrate trajectory.
    """

    def __init__(
            self,
            system=lorenz_96,
            int_method=integrators.RungeKutta4(),
            system_state=SystemState(),
            increment: float = 0.01,
            forcing=forcings.ConstantForcing()
    ):
        """
        :param system: first-order differential equations system
        :param int_method: integration method
        :param: system_state: instance of SystemState class
        :param: increment: time increment (dt)
        :param: forcing: external forcing
        """
        self.system = system
        self.int_method = int_method
        self.system_state = system_state
        self.increment = increment
        self.forcing = forcing

        self.init_time = self.system_state.time

    def __repr__(self):
        return "\nsystem model: {}\n" \
               "integration method: {}\n" \
               "time increment: {}\n" \
               "forcing: {}\n\n" \
               "--- system state ---\n" \
               "coordinates: {}\n" \
               "time: {}\n".format(
            self.system,
            self.int_method,
            self.increment,
            self.forcing,
            self.system_state.coords,
            self.system_state.time
        )

    def integrate(self, integration_time=None):
        """
        Evolve the state of system_state till **integration_time**, which automatically update the state of point.

        :param integration_time: total time of integration. If None, integrate to the next time step.
        :return: None
        """
        if integration_time is None:
            integration_time = self.increment

        integration_steps = int(integration_time/self.increment)

        for _ in np.arange(0, integration_steps):
            self.system_state.coords = self.int_method(
                self.system_state.coords,
                self.forcing(self.system_state.time),
                self.system,
                self.increment
            )
            self.system_state.time = round(self.system_state.time + self.increment, 2)

    def integrate_one_step(self):
        """
        Evolve the state of system_state till the next time step, which automatically update the state of point.

        :return: None
        """

        self.system_state.coords = self.int_method(
            self.system_state.coords,
            self.forcing(self.system_state.time),
            self.system,
            self.increment
        )
        self.system_state.time = round(self.system_state.time + self.increment, 2)


class SimulationRunner:

    def __init__(
            self,
            simulator: Simulator = Simulator(),
    ):
        """
        :param simulator: Simulator() instance
        :return
        """
        self.simulator = simulator

    def __create_dataset(self,
                         outfile_name: str,
                         nodes: int,
                         ):
        """
        This method create writeable netcdf dataset
        :param outfile_name: name of the file
        :return:
        """
        dataset = nc.Dataset(outfile_name, 'w')

        dataset.createDimension('node', nodes)
        dataset.createDimension('time', None)

        dataset.createVariable('time', np.float64, ('time',))
        dataset.createVariable('node', np.int32, ('node',))

        dataset.createVariable('var', np.float32, ('time', 'node'))

        dataset.variables['node'][:] = np.arange(0, nodes)

        return dataset

    def __init_netcdf(self,
                      write_all_every: float = 0,
                      ):
        """
        Initialize netcdf to write output.
        :param write_all_every: if 0, write only node 0; else, write all every **write_all_every** iterations.
        :return:
        """

        if write_all_every == 0:

            # write only one node

            #outfile_name = ''
            dataset = self.__create_dataset(outfile_name, 1)

            dataset = [dataset]

        else:

            # write always one node and all nodes every time **time** is multiple of **write_all_every**
            # (need two output datasets)

            dim = len(self.simulator.system_state.coords)
            #outfile_name_all = ''
            dataset_all = self.__create_dataset(outfile_name_all, dim)
            #outfile_name_one = ''
            dataset_one = self.__create_dataset(outfile_name_one, 1)

            dataset = [dataset_one, dataset_all]

        return dataset

    def run(
            self,
            out_file: str,
            integration_time: int = 10000,
            chunk_length: int = 1000,
            write_all_every: int = 0,
    ):
        """
        Run the simulation
        :param out_file: path to output file
        :param integration_time: total time of integration
        :param chunk_length: integration steps after which write on netcdf and free memory.
        :param write_all_every: if 0, write only node 0; else, write all nodes when time is multiple of
        **write_all_every**.
        :return:
        """

        integration_steps = int(integration_time / self.simulator.increment)
        chunks = int(integration_steps / chunk_length)

        # remove out file if already exists
        if os.path.exists(out_file):
            os.remove(out_file)

        dataset = self.__init_netcdf(write_all_every)

        for chunk in np.arange(0, chunks):
            dim = len(self.simulator.system_state.coords)
            t = []
            data_array = np.empty((chunk_length, dim))
            # simulate one chunk
            for i in np.arange(0, chunk_length):
                data_array[i, :] = self.simulator.system_state.coords
                t.append(self.simulator.system_state.time)
                self.simulator.integrate_one_step()
            # write
            dataset[0].variables['var'][(chunk_length * chunk):(chunk_length * (chunk + 1)), 0] = data_array[:, 0]
            dataset[0].variables['time'][(chunk_length * chunk):(chunk_length * (chunk + 1))] = t

            if write_all_every:
                indices = [i for i in range(0, chunk_length, write_all_every)]
                data_array_all = data_array_all[indices, :]
                t_all = t[indices]
                dataset[1].variables['var'][0][(len(indices) * chunk):(len(indices) * (chunk + 1)), :] = data_array_all
                dataset[1].variables['time'][(len(indices) * chunk):(len(indices) * (chunk + 1))] = t_all
