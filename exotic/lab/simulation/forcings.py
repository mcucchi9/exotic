import math


class Forcing:

    @property
    def short_name(self):
        return self._short_name

    @property
    def long_name(self):
        return self._long_name


class ConstantForcing(Forcing):
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

        self._short_name = 'CF_{}'.format(force_intensity)
        self._long_name = 'Constant Forcing ({})'.format(force_intensity)

    def __call__(
            self,
            time: float
    ):
        return self.force_intensity


class DeltaForcing(Forcing):
    """
    Define delta forcing. A constant forcing **force_intensity_base** is applied throughout the whole dynamic,
    except for t=**activation_time**, at which a force equal to **force_intensity_base** + **force_intensity_delta**
    is applied.
    """
    def __init__(
            self,
            activation_time: float = 0,
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

        self._short_name = 'DF_{}_{}_{}'.format(
            self.force_intensity_base,
            self.force_intensity_delta,
            self.activation_time,
        )
        self._long_name = 'Delta Forcing ({}+{} at t={})'.format(
            self.force_intensity_base,
            self.force_intensity_delta,
            self.activation_time,
        )

    def __call__(
            self,
            time: float
    ):
        force = self.force_intensity_base + self.force_intensity_delta*math.isclose(time, self.activation_time)
        return force


class StepForcing(Forcing):
    """
    Define step forcing. A constant forcing **force_intensity_base** is applied till before **activation_time**,
    while from t=**activation_time** a force equal to **force_intensity_base** + **force_intensity_delta**
    is applied.
    """
    def __init__(
            self,
            activation_time: float = 0,
            force_intensity_base: float = 8.0,
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

        self._short_name = 'SF_{}_{}_{}'.format(
            self.force_intensity_base,
            self.force_intensity_delta,
            self.activation_time,
        )
        self._long_name = 'Step Forcing ({}+{} at t={})'.format(
            self.force_intensity_base,
            self.force_intensity_delta,
            self.activation_time,
        )

    def __call__(
            self,
            time: float
    ):
        force = self.force_intensity_base + self.force_intensity_delta*(time >= self.activation_time)
        return force


class LinearForcing(Forcing):
    """
    Define linear forcing. A constant forcing **force_intensity_base** is applied till before **activation_time**,
    while from t=**activation_time** a linear force of the form F = **linear_coefficient** * t +
    **force_intensity_base** is applied till **deactivation_time**.
    """
    def __init__(
            self,
            activation_time: float = 0,
            deactivation_time: float = 100,
            force_intensity_base: float = 8,
            linear_coefficient: float = 0.001
    ):
        """
        :param activation_time: time at which forcing is activated
        :param deactivation_time: time at which forcing is deactivated
        :param force_intensity_base: starting force
        :param linear_coefficient: linear coefficient (referred to real simulation time)
        """
        self.activation_time = activation_time
        self.deactivation_time = deactivation_time
        self.force_intensity_base = force_intensity_base
        self.linear_coefficient = linear_coefficient

        self._short_name = 'LF_{}_{}_{}_{}'.format(
            self.force_intensity_base,
            self.linear_coefficient,
            self.activation_time,
            self.deactivation_time
        )
        self._long_name = 'Linear Forcing ({}+{}*t, starting at t={} and ending at t={})'.format(
            self.force_intensity_base,
            self.linear_coefficient,
            self.activation_time,
            self.deactivation_time
        )

    def __call__(
            self,
            time: float
    ):

        if time <= self.activation_time:
            force = self.force_intensity_base
        elif self.activation_time < time <= self.deactivation_time:
            force = self.force_intensity_base + self.linear_coefficient * (time - self.activation_time)
        else:
            force = self.force_intensity_base + self.linear_coefficient * \
                    (self.deactivation_time - self.activation_time)

        return force


class SinusoidalForcing(Forcing):
    """
    Define sinusoidal forcing. A constant forcing **force_intensity_base** is applied till before **activation_time**,
    while from t=**activation_time** a sinusoidal force of the form
    F = **epsilon** * sin(**omega** * t)
    is applied till **deactivation_time**.
    """
    def __init__(
            self,
            activation_time: float = 0,
            deactivation_time: float = 100,
            force_intensity_base: float = 8,
            epsilon: float = 1,
            omega: float = 0.1,
    ):
        """
        :param activation_time: time at which forcing is activated
        :param deactivation_time: time at which forcing is deactivated
        :param force_intensity_base: starting force
        :param epsilon: sine amplitude
        :param omega: angular frequency (referred to real simulation time)
        """
        self.activation_time = activation_time
        self.deactivation_time = deactivation_time
        self.force_intensity_base = force_intensity_base
        self.epsilon = epsilon
        self.omega = omega

        self._short_name = 'SinF_{}_{}_{}_{}_{}'.format(
            self.force_intensity_base,
            self.epsilon,
            self.omega,
            self.activation_time,
            self.deactivation_time
        )
        self._long_name = 'Sinusoidal Forcing ({}*sin({}*t), starting at t={} and ending at t={})'.format(
            self.force_intensity_base,
            self.epsilon,
            self.omega,
            self.activation_time,
            self.deactivation_time
        )

    def __call__(
            self,
            time: float
    ):

        if time <= self.activation_time:
            force = self.force_intensity_base
        elif self.activation_time < time <= self.deactivation_time:
            force = self.force_intensity_base + self.epsilon * math.sin(self.omega * (time - self.activation_time))
        else:
            force = self.force_intensity_base + self.epsilon * \
                    math.sin(self.omega * (self.deactivation_time - self.activation_time))

        return force

