import numpy as np


class System:

    # def __init__(self, x, f, fx, hs):
    #     """
    #     Initialize integration method
    #     :param x: coordinates at time t0
    #     :param f: external forcing
    #     :param fx: first-order differential equations system.
    #     :param hs: time increment (dt)
    #     """
    #     self.x = x
    #     self.f = f
    #     self.fx = fx
    #     self.hs = hs

    pass


class Lorenz96(System):

    @property
    def short_name(self):
        return 'lorenz96'

    @property
    def long_name(self):
        return 'Lorenz 96'

    def __call__(self, x, forcing):
        """
        This method implement Lorenz-96 first-order differential equations system.
        :param x: coordinates at time t0
        :param forcing: (constant) forcing term
        :return: state derivatives at time t0
        """
        n = len(x)

        d = np.zeros(n)

        for i in range(0, n):
            d[i] = (x[(i + 1) % n] - x[i - 2]) * x[i - 1] - x[i] + forcing

        return d