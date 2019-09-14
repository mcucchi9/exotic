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
            integration_time: int = 10000,
            chunk_length_time: int = 1000,
            write_all_every: float = 0,
            write_one_every: float = None,
    ):
        """
        :param simulator: Simulator() instance
        :param integration_time: total time of integration
        :param chunk_length: integration steps after which write on netcdf and free memory.
        :param write_all_every: if 0, never write all nodes; else, write all nodes when time is multiple of
        **write_all_every**.
        :param write_one_every: if 0, never write one node; else, write one nodee when time is multiple of
        **write_all_every**.
        :return
        """
        self.simulator = simulator
        self.integration_time = integration_time
        self.chunk_length = int(chunk_length_time / self.simulator.increment)
        self.write_all_every = write_all_every
        self.write_one_every = write_one_every
        if self.write_one_every is None:
            self.write_one_every = self.simulator.increment
        # write_all_* from time to iterations
        self.write_all_every_iter = int(self.write_all_every / self.simulator.increment)
        self.write_one_every_iter = int(self.write_one_every / self.simulator.increment)

    def _create_dataset(
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

    def _create_outfile_name(
            self,
            custom_suffix: str = '00000'
    ) -> dict:

        outfile_name_base = 'sim/{system}/{integrator}/t_1_00/{forcing}/sim_{system}_{integrator}_{forcing}'.format(
            system=self.simulator.system.short_name,
            integrator=self.simulator.int_method.short_name,
            forcing=self.simulator.forcing.short_name
        )

        outfile_name = {}

        if self.write_one_every_iter:
            outfile_name_one = '{}_one_{}.nc'.format(outfile_name_base, custom_suffix)
            outfile_name['one'] = outfile_name_one
        if self.write_all_every_iter:
            outfile_name_all = '{}_all_{}.nc'.format(outfile_name_base, custom_suffix)
            outfile_name['all'] = outfile_name_all

        return outfile_name

    def _init_netcdf(
            self,
            outfile_names: dict,
            custom_attrs: dict = {},
    ) -> dict:
        """
        Initialize netcdf to write output.
        :return:
        """

        datasets = {}

        if self.write_one_every_iter:
            dataset_one = self._create_dataset(outfile_names['one'], 1, custom_attrs)
            datasets['one'] = dataset_one
        if self.write_all_every_iter:
            dim = len(self.simulator.system_state.coords)
            dataset_all = self._create_dataset(outfile_names['all'], dim, custom_attrs)
            datasets['all'] = dataset_all

        return datasets

    def run(
            self,
            data_base_path: str = DATA_BASE_PATH,
            custom_suffix: str = '00000',
            custom_attrs: dict = {},
    ):
        """
        Run the simulation and write the output to a netcdf file.
        The two functions are blend together because I make use of the ability to write while running (writing every
        N iterations). Maybe it would be better to split the functions in different methods.
        :param data_base_path: base path were data are going to be saved
        :param custom_suffix: suffix to the out file name
        :param custom_attrs: attributes to be added to the netcdf
        :return:
        """

        if self.write_one_every is None:
            self.write_one_every = self.simulator.increment

        integration_steps = int(self.integration_time / self.simulator.increment)
        chunks = int(integration_steps / self.chunk_length)

        outfiles = self._create_outfile_name(custom_suffix)
        outfiles = {key: os.path.join(data_base_path, outfile) for key, outfile in outfiles.items()}

        # check if dir exists. if not, create it.
        # else remove out file if already exists
        for outfile in outfiles.values():
            if not os.path.exists(os.path.dirname(outfile)):
                os.makedirs(os.path.dirname(outfile))
            elif os.path.exists(outfile):
                os.remove(outfile)

        datasets = self._init_netcdf(
            outfile_names=outfiles,
            custom_attrs=custom_attrs
        )

        count = 0

        for chunk in np.arange(0, chunks):
            dim = len(self.simulator.system_state.coords)
            t = []
            data_array = np.empty((self.chunk_length, dim))
            # simulate one chunk
            for i in np.arange(0, self.chunk_length):
                data_array[i, :] = self.simulator.system_state.coords
                t.append(i+chunk*self.chunk_length)
                self.simulator.integrate_one_step()
                count += 1
            # write on file
            if self.write_one_every_iter:
                if self.chunk_length >= self.write_one_every_iter:
                    indices = [i for i in range(0, self.chunk_length, self.write_one_every_iter)]
                    data_array_one = data_array[indices, 0]
                    t_one = [t[i] for i in indices]
                    datasets['one'].variables['var'][(len(indices) * chunk):(len(indices) * (chunk + 1)), :] = \
                        data_array_one
                    datasets['one'].variables['time_step'][(len(indices) * chunk):(len(indices) * (chunk + 1))] = t_one
                elif count >= self.write_one_every_iter:
                    index = self.write_one_every_iter - chunk * self.chunk_length
                    data_array_one = data_array[index, 0]
                    t_one = t[index]
                    datasets['one'].variables['var'][index] = data_array_one
                    datasets['one'].variables['time_step'][index] = t_one
            if self.write_all_every_iter:
                if self.chunk_length >= self.write_all_every_iter:
                    indices = [i for i in range(0, self.chunk_length, self.write_all_every_iter)]
                    data_array_all = data_array[indices, :]
                    t_all = [t[i] for i in indices]
                    datasets['all'].variables['var'][(len(indices) * chunk):(len(indices) * (chunk + 1)), :] = \
                        data_array_all
                    datasets['all'].variables['time_step'][(len(indices) * chunk):(len(indices) * (chunk + 1))] = t_all
                elif count >= self.write_all_every_iter:
                    index = self.write_all_every_iter - chunk * self.chunk_length
                    data_array_all = data_array[index, 0]
                    t_all = t[index]
                    datasets['one'].variables['var'][index] = data_array_all
                    datasets['one'].variables['time_step'][index] = t_all

        if datasets:
            for dataset in datasets.values():
                dataset.close()

        return outfiles
