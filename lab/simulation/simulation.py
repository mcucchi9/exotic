import numpy as np
import netCDF4 as nc
import os
import datetime

from . import forcings
from . import integrators
from . import systems

DATA_BASE_PATH = '../../../../data/'


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
            system=systems.Lorenz96(),
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
            self.system.long_name,
            self.int_method.long_name,
            self.increment,
            self.forcing.long_name,
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

    def __create_dataset(
            self,
            outfile_name: str,
            nodes: int,
            custom_attrs: dict = {},
    ):
        """
        This method create writeable netcdf dataset
        :param outfile_name: name of the file
        :return:
        """
        dataset = nc.Dataset(outfile_name, 'w', format='NETCDF4_CLASSIC')

        dataset.createDimension('node', nodes)
        dataset.createDimension('time_step', None)

        dataset.createVariable('node', np.int32, ('node',))
        dataset.createVariable('time_step', np.int32, ('time_step',))

        var = dataset.createVariable('var', np.float32, ('time_step', 'node'))

        dataset.variables['node'][:] = np.arange(0, nodes)

        # Attributes
        var.system = self.simulator.system.long_name
        var.integration_method = self.simulator.int_method.long_name
        var.integration_step = self.simulator.increment
        var.forcing = self.simulator.forcing.long_name
        var.created = str(datetime.datetime.now())

        for attr_key, attr_value in custom_attrs.items():
            var.setncattr(attr_key, attr_value)

        return dataset

    def __create_outfile_name(
            self,
            write_all_every,
            custom_suffix
    ):

        outfile_name_base = 'sim/{system}/{integrator}/{forcing}/sim_{system}_{integrator}_{forcing}'.format(
            system=self.simulator.system.short_name,
            integrator=self.simulator.int_method.short_name,
            forcing=self.simulator.forcing.short_name
        )
        outfile_name_one = '{}_one_{}.nc'.format(outfile_name_base, custom_suffix)
        if write_all_every:
            outfile_name_all = '{}_all_{}.nc'.format(outfile_name_base, custom_suffix)
            outfile_name = [outfile_name_one, outfile_name_all]
        else:
            outfile_name = [outfile_name_one]

        return outfile_name

    def __init_netcdf(
            self,
            outfile_name: list,
            write_all_every: float = 0,
            custom_attrs: dict = {},
    ):
        """
        Initialize netcdf to write output.
        :param write_all_every: if 0, write only node 0; else, write all every **write_all_every** iterations.
        :return:
        """

        if write_all_every == 0:

            # write only one node

            dataset = self.__create_dataset(outfile_name[0], 1, custom_attrs)

            dataset = [dataset]

        else:

            # write always one node and all nodes every time **time** is multiple of **write_all_every**
            # (need two output datasets)

            dim = len(self.simulator.system_state.coords)
            dataset_one = self.__create_dataset(outfile_name[0], 1, custom_attrs)
            dataset_all = self.__create_dataset(outfile_name[1], dim, custom_attrs)

            dataset = [dataset_one, dataset_all]

        return dataset

    def run(
            self,
            integration_time: int = 10000,
            chunk_length: int = 1000,
            write_all_every: float = 0,
            data_base_path: str = DATA_BASE_PATH,
            custom_suffix: str = '00000',
            custom_attrs: dict = {},
    ):
        """
        Run the simulation
        :param integration_time: total time of integration
        :param chunk_length: integration steps after which write on netcdf and free memory.
        :param write_all_every: if 0, write only node 0; else, write all nodes when time is multiple of
        **write_all_every**.
        :param data_base_path: base path were data are going to be saved
        :param custom_suffix: suffix to the out file name
        :param custom_attrs: attributes to be added to the netcdf
        :return:
        """

        integration_steps = int(integration_time / self.simulator.increment)
        chunks = int(integration_steps / chunk_length)

        # write_all_every from time to iterations
        write_all_every = int(write_all_every / self.simulator.increment)

        outfiles = self.__create_outfile_name(write_all_every, custom_suffix)
        outfiles = [os.path.join(data_base_path, outfile) for outfile in outfiles]

        # check if dir exists. if not, create it.
        for outfile in outfiles:
            if not os.path.exists(os.path.dirname(outfile)):
                os.makedirs(os.path.dirname(outfile))

        # remove out file if already exists
        for file_path in outfiles:
            if os.path.exists(file_path):
                os.remove(file_path)

        dataset = self.__init_netcdf(
            write_all_every=write_all_every,
            outfile_name=outfiles,
            custom_attrs=custom_attrs
        )

        for chunk in np.arange(0, chunks):
            dim = len(self.simulator.system_state.coords)
            t = []
            data_array = np.empty((chunk_length, dim))
            # simulate one chunk
            for i in np.arange(0, chunk_length):
                data_array[i, :] = self.simulator.system_state.coords
                t.append(i+chunk*chunk_length)
                self.simulator.integrate_one_step()
            # write
            dataset[0].variables['var'][(chunk_length * chunk):(chunk_length * (chunk + 1)), 0] = data_array[:, 0]
            dataset[0].variables['time_step'][(chunk_length * chunk):(chunk_length * (chunk + 1))] = t

            if write_all_every:
                indices = [i for i in range(0, chunk_length, write_all_every)]
                data_array_all = data_array[indices, :]
                t_all = [t[i] for i in indices]
                dataset[1].variables['var'][(len(indices) * chunk):(len(indices) * (chunk + 1)), :] = data_array_all
                dataset[1].variables['time_step'][(len(indices) * chunk):(len(indices) * (chunk + 1))] = t_all

        for d in dataset:
            d.close()

        return outfiles
