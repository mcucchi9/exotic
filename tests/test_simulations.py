import pytest
import numpy as np
from lab import simulation


def toy_system(x, forcing):

    x = np.asarray(x)
    d = 5*x + forcing

    return d


@pytest.mark.parametrize("input_coord, input_forcing, input_system, input_increment, expected", [
    ([0, 0, 0], 0, toy_system, 0.1, [0, 0, 0]),
    ([1, 1, 1], 0, toy_system, 0.1, [1.6484375, 1.6484375, 1.6484375]),
])
def test_runge_kutta_4(input_coord, input_forcing, input_system, input_increment, expected):

    result = simulation.runge_kutta_4(input_coord, input_forcing, input_system, input_increment)

    assert all([a == b for a, b in zip(result, expected)])


@pytest.mark.parametrize("input_coord, input_forcing, expected", [
    ([0, 0, 0], 0, [0, 0, 0]),
    ([1, 2, 3], 0, [-1, -2, -3]),
    ([1, 2, 3], 1, [0, -1, -2]),
    ([1, 2, 3, 4], 0, [-5, -3, 3, -7]),
])
def test_lorenz_96(input_coord, input_forcing, expected):

    result = simulation.lorenz_96(input_coord, input_forcing)

    print(result)

    assert all([a == b for a, b in zip(result, expected)])


def test_SystemState_repr():

    point = simulation.SystemState(coords=[1, 2, 3], time=2)
    result = point.__repr__()
    expected = 'coordinates: [1, 2, 3]\n' \
               'time: 2'


def test_SystemState_energy():

    point = simulation.SystemState(coords=[1, 1, 1])
    result = point.energy
    expected = 1.5

    assert result == expected


