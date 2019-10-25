class IntegrationMethod:

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

class RungeKutta4(IntegrationMethod):

    @property
    def short_name(self):
        return 'rk4'

    @property
    def long_name(self):
        return 'Runge-Kutta 4th order'

    def __call__(self, x, f, fx, hs):
        """
        This method implement 4th order Runge-Kutta integration method.
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
