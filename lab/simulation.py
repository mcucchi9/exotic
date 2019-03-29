import numpy as np
import netCDF4 as nc
import os
import math


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


class ConstantForcing:
    """
    Define constant forcing, equal to **force_intensity**
    """

    def __init__(
            self,
            force_intensity: float = 8,
    ):
        """
        :param force_intensity: intensity of force
        """
        self.force_intensity = force_intensity

    def __call__(
            self,
            time: float
    ):
        return self.force_intensity


class DeltaForcing:
    """
    Define delta forcing. A constant forcing **force_intensity_base** is applied throughout the whole dynamic,
    except for t=**activation_time**, at which a force equal to **force_intensity_base** + **force_intensity_delta**
    is applied.
    """
    def __init__(
            self,
            activation_time: float,
            force_intensity_base: float = 8,
            force_intensity_delta: float = 0.5
    ):
        """
        :param activation_time: time at which force_intensity_delta is activated
        :param force_intensity_base: base constant forcing
        :param force_intensity_delta: force spike applied at activation_time
        """
        self.activation_time = activation_time
        self.force_intensity_base = force_intensity_base
        self.force_intensity_delta = force_intensity_delta

    def __call__(
            self,
            time: float
    ):
        force = self.force_intensity_base + self.force_intensity_delta*math.isclose(time, self.activation_time)
        return force


class StepForcing:
    """
    Define step forcing. A constant forcing **force_intensity_base** is applied till before **activation_time**,
    while from t=**activation_time** a force equal to **force_intensity_base** + **force_intensity_delta**
    is applied.
    """
    def __init__(
            self,
            activation_time: float,
            force_intensity_base: float = 8,
            force_intensity_delta: float = 0.5
    ):
        """
        :param activation_time: time at which force_intensity_delta is activated
        :param force_intensity_base: base constant forcing
        :param force_intensity_delta: force spike applied at activation_time
        """
        self.activation_time = activation_time
        self.force_intensity_base = force_intensity_base
        self.force_intensity_delta = force_intensity_delta

    def __call__(
            self,
            time: float
    ):
        force = self.force_intensity_base + self.force_intensity_delta*(time >= self.activation_time)
        return force


class Simulator:
    """
    Integrate point and system information,
    """

    def __init__(
            self,
            system=lorenz_96,
            int_method=runge_kutta_4,
            system_state=SystemState(),
            increment: float = 0.01,
            forcing=ConstantForcing()
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

    def __init_netcdf(self, dataset, write_all):

        dim = len(self.simulator.system_state.coords)

        if write_all:
            dataset.createDimension('node', dim)
            dataset.createDimension('time', None)

            times = dataset.createVariable('time', np.float64, ('time',))
            nodes = dataset.createVariable('node', np.int32, ('node',))

            var = dataset.createVariable('var', np.float32, ('time', 'node'))
            nodes[:] = np.arange(0, dim)
        else:
            dataset.createDimension('node', 1)
            dataset.createDimension('time', None)

            times = dataset.createVariable('time', np.float64, ('time',))
            nodes = dataset.createVariable('node', np.int32, ('node',))

            var = dataset.createVariable('var', np.float32, ('time', 'node'))
            nodes[:] = np.arange(0, 1)

        return var, times, dim

    def run(
            self,
            out_file: str,
            integration_time: int = 10000,
            chunk_length: int = 1000,
            write_all: bool = False,
    ):
        """
        Run the simulation
        :param out_file: path to output file
        :param integration_time:
        :param chunk_length:
        :param write_all:
        :return:
        """

        integration_steps = int(integration_time / self.simulator.increment)
        chunks = int(integration_steps / chunk_length)

        # remove out file if already exists
        if os.path.exists(out_file):
            os.remove(out_file)

        with nc.Dataset(out_file, 'w') as dataset:

            var, times, dim = self.__init_netcdf(dataset, write_all)

            for chunk in np.arange(0, chunks):
                # initialize chunk numpy array
                t = []
                data_array = np.empty((chunk_length, dim))
                # simulate one chunk
                for i in np.arange(0, chunk_length):
                    data_array[i, :] = self.simulator.system_state.coords
                    t.append(self.simulator.system_state.time)
                    self.simulator.integrate_one_step()
                # write
                if write_all:
                    var[(chunk_length * chunk):(chunk_length * (chunk + 1)), :] = data_array
                else:
                    var[(chunk_length * chunk):(chunk_length * (chunk + 1)), 0] = data_array[:, 0]
                times[(chunk_length * chunk):(chunk_length * (chunk + 1))] = t

