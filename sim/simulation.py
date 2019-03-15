import numpy as np
import netCDF4 as nc
import os


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

    def __init__(self,
                 coords=(0, 0, 0),
                 time=0
                 ):
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

    def perturb(self, intensity=0.05):

        random_seed = 1234

        np.random.seed(random_seed)
        perturbation = np.random.uniform(-intensity, intensity, size=len(self.coords))

        self.coords += perturbation


class Simulator:
    """
    Integrate point and system information,
    """

    def __init__(self,
                 system=lorenz_96,
                 int_method=runge_kutta_4,
                 system_state=SystemState(),
                 increment=0.01,
                 forcing=0
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
               "time: {}\n".format(self.system,
                                   self.int_method,
                                   self.increment,
                                   self.forcing,
                                   self.system_state.coords,
                                   self.system_state.time
                                   )

    def integrate(self, integration_time=None):
        """
        Evolve the state of system_state, which automatically update the state of point.

        :param integration_time: total time of integration. If None, integrate to the next time step.
        :return: None
        """
        if integration_time is None:
            integration_time = self.increment

        integration_steps = int(integration_time/self.increment)

        for _ in np.arange(0, integration_steps):
            self.system_state.coords = self.int_method(self.system_state.coords, self.forcing,
                                                       self.system, self.increment)
            self.system_state.time = self.system_state.time + self.increment


class SimulationRunner:

    def __init__(self,
                 simulator: Simulator,
                 integration_time: int,
                 chunk_length: int,
                 out_file: str):
        """
        :param simulator: Simulator() instance
        :param integration_time: total time of integration
        :param chunk_length: length of each chunk (computed before saving to file), in terms of integration steps
        :param out_file: path to output file
        :return
        """
        self.simulator = simulator
        self.integration_time = integration_time
        self.chunk_length = chunk_length
        self.out_file = out_file
        self.integration_steps = int(self.integration_time / simulator.increment)
        self.chunks = int(self.integration_steps / self.chunk_length)

    def __init_netcdf(self,
                      dataset):

        dim = len(self.simulator.system_state.coords)

        dataset.createDimension('node', dim)
        dataset.createDimension('time', None)

        times = dataset.createVariable('time', np.float64, ('time',))
        nodes = dataset.createVariable('node', np.int32, ('node',))

        var = dataset.createVariable('var', np.float32, ('time', 'node'))
        nodes[:] = np.arange(0, dim)

        return var, times, dim

    def run(self):

        # remove out file if already exists
        if os.path.exists(self.out_file):
            os.remove(self.out_file)

        with nc.Dataset(self.out_file, 'w') as dataset:

            var, times, dim = self.__init_netcdf(dataset)

            for chunk in np.arange(0, self.chunks):
                # initialize chunk numpy array
                t = []
                data_array = np.empty((self.chunk_length, dim))
                # simulate one chunk
                for i in np.arange(0, self.chunk_length):
                    data_array[i, :] = self.simulator.system_state.coords
                    t.append(self.simulator.system_state.time)
                    self.simulator.integrate()
                # write
                var[(self.chunk_length * chunk):(self.chunk_length * (chunk + 1)), :] = data_array
                times[(self.chunk_length * chunk):(self.chunk_length * (chunk + 1))] = t
