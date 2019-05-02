import math

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