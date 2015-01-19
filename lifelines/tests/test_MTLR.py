# py.test MTLR


import numpy as np
from numpy import exp, log
import pytest
import numpy.testing as npt


@pytest.fixture
def T():
    return np.array([0, 1, 2])


@pytest.fixture
def Theta():
    return np.array([[-0.5, -0.2],
                     [0.2, 0.1],
                     [0.3, -0.1]])


@pytest.fixture
def X():
    return np.array([[1, 1],
                     [2, 0],
                     [1, -1]])


def test_sum_exp_f(X, T, Theta):
    x = X[0, :]

    assert mtlr._sum_exp_f(Theta, x, 0) == np.exp(mtlr._f(Theta, x, 0))
    assert mtlr._sum_exp_f(Theta, x, 1) == np.exp(mtlr._f(Theta, x, 0)) + np.exp(mtlr._f(Theta, x, 1))


def test_d_log_likelihood_j(X, T, Theta):
    X = X[0, :].reshape(1, 2)
    x = X[0, :]
    expected = 1 * x - mtlr._sum_exp_f(Theta, x, 0) / mtlr._sum_exp_f(Theta, x, 3) * x
    actual = mtlr._d_log_likelihood_j(Theta, X, 0, T)

    npt.assert_array_almost_equal(expected, actual)


def test_coef_norm(Theta):
    assert (mtlr._coef_norm(Theta) - (Theta ** 2).sum()) < 10e-10


def test_smoothing_norm(Theta):
    assert abs(mtlr._smoothing_norm(Theta) - (((Theta[1, :] - Theta[0,:])**2).sum() +\
                                   ((Theta[2, :] - Theta[1,:])**2).sum())) < 10e-10


def test_first_part_log_likelihood_j(Theta, X, T):
    j = 0
    actual = mtlr._first_part_log_likelihood_j(Theta, X, T, j)
    expected = np.array([-0.5, -0.2]).dot([1, 1])
    assert abs(actual - expected) < 10e-5

    j = 1
    actual = mtlr._first_part_log_likelihood_j(Theta, X, T, j)
    expected = np.array([0.2, 0.1]).dot([1, 1]) + np.array([0.2, 0.1]).dot([2, 0])
    assert abs(actual - expected) < 10e-5


def test_second_part_log_likelihood(Theta, X):
    actual = mtlr._second_part_log_likelihood(Theta, X)
    expected = np.log(exp(mtlr._f(Theta, X[0, :], 0)) + exp(mtlr._f(Theta, X[0,:], 1)) + exp(mtlr._f(Theta, X[0,:], 2)) + exp(mtlr._f(Theta, X[0,:], 3))) +\
               np.log(exp(mtlr._f(Theta, X[1, :], 0)) + exp(mtlr._f(Theta, X[1,:], 1)) + exp(mtlr._f(Theta, X[1,:], 2)) + exp(mtlr._f(Theta, X[0,:], 3))) +\
               np.log(exp(mtlr._f(Theta, X[2, :], 0)) + exp(mtlr._f(Theta, X[2,:], 1)) + exp(mtlr._f(Theta, X[2,:], 2)) + exp(mtlr._f(Theta, X[0,:], 3)))
    assert abs(expected - actual) < 10e-5


def test_simplest_minimizing_function():
    Theta = np.array([[1.]])
    T = np.array([[0.]])
    X = np.array([[1.]])
    assert mtlr._smoothing_norm(Theta) == 0.0
    assert mtlr._coef_norm(Theta) == 1.0
    assert mtlr._log_likelihood(Theta, X, T) == (1 - np.log(np.exp(1) + 1))

    assert mtlr._minimizing_function(Theta, X, T, 1., 1.) == 0.5 - (1 - np.log(np.exp(1) + 1))

    Theta = np.array([[1.], [1.]])
    T = np.array([0., 1.])
    X = np.array([[1.], [-1.]])

    npt.assert_approx_equal(0.5 * 1. * mtlr._coef_norm(Theta), 0.5 * (1. + 1.))
    npt.assert_approx_equal(0.5 * 1. * mtlr._smoothing_norm(Theta), 0.)
    npt.assert_approx_equal(mtlr._first_part_log_likelihood_j(Theta, X, T, 0),  (1*Theta[0, :]*X[0,:] + 0*Theta[0,:]*X[1,:]))
    npt.assert_approx_equal(mtlr._first_part_log_likelihood_j(Theta, X, T, 1),  (1*Theta[1, 0]*X[0, :] + 1*Theta[1,:]*X[1,:]))
    npt.assert_approx_equal(mtlr._second_part_log_likelihood(Theta, X),  np.log(exp(2) + exp(1) + exp(0)) + np.log(exp(0) + exp(-1) + exp(-2)))
    npt.assert_approx_equal(mtlr._log_likelihood(Theta, X, T),  (1 + 1 - np.log(exp(2) + exp(1) + exp(0))) + (0 - 1 - np.log(exp(0) + exp(-1) + exp(-2))))