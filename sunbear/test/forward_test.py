from functools import reduce
import numpy as np
import pytest
import sunbear as sb
import matplotlib.pyplot as plt

############################## case: no potential ##############################

def test_forward_1d_no_pot():
    _test_forward_nd_no_pot(n=100, ndim=1)

def test_forward_2d_no_pot():
    _test_forward_nd_no_pot(n=100, ndim=2)

def test_forward_3d_no_pot():
    _test_forward_nd_no_pot(n=30, ndim=3)

def test_forward_4d_no_pot():
    _test_forward_nd_no_pot(n=10, ndim=4)

def _test_forward_nd_no_pot(n, ndim):
    x = np.linspace(-1, 1, n)
    xs = np.meshgrid([x]*ndim, indexing="ij")
    xs_sq = reduce(lambda x,y:x+y*y, xs, 0.0)

    source = np.exp(-xs_sq / (2*0.2**2))
    source_copy = np.copy(source)
    phi = np.zeros_like(source)

    # target should be the same as source, as there's no potential
    target = sb.forward(source, phi)
    assert source == pytest.approx(target)

    # make sure the source is not changed
    assert np.all(source == source_copy)

########################### case: slanted potential ###########################
def test_forward_1d_slanted_pot():
    _test_forward_nd_slanted_pot(n=100, ndim=1)

def test_forward_2d_slanted_pot():
    _test_forward_nd_slanted_pot(n=100, ndim=2)

def test_forward_3d_slanted_pot():
    _test_forward_nd_slanted_pot(n=20, ndim=3)

def _test_forward_nd_slanted_pot(n, ndim, abs=None):
    x = np.arange(n) - n / 2.0
    xs = np.meshgrid(*([x]*ndim), indexing="ij")
    xs_sq = reduce(lambda x,y:x+y*y, xs, 0.0)

    # phi is slanted on the first dimension, so the target will be shifted
    # source on the first dimension by A
    A = n / 6.0
    sigma = (n/30.)
    source = np.exp(-xs_sq / (2*sigma**2))
    source_copy = np.copy(source)
    phi = xs[0] * A
    target = sb.forward(source, phi)

    xs2 = np.copy(xs)
    xs2[0] -= A
    xs2_sq = reduce(lambda x,y:x+y*y, xs2, 0.0)
    target_calc = np.exp(-xs2_sq / (2*sigma**2))

    # accurate within 2.5*(1/n)*100%
    abs = 2.5/n if abs is None else abs
    assert target == pytest.approx(target_calc, abs=abs)

    # check the dimension of target
    assert np.ndim(target) == ndim

    # make sure the source is not changed
    assert np.all(source == source_copy)

########################## case: quadratic potential ##########################
def test_forward_1d_quad_pot():
    _test_forward_nd_quad_pot(n=100, ndim=1)

def test_forward_2d_quad_pot():
    _test_forward_nd_quad_pot(n=100, ndim=2)

def test_forward_3d_quad_pot():
    _test_forward_nd_quad_pot(n=20, ndim=3)

def _test_forward_nd_quad_pot(n, ndim, abs=None):
    x = np.arange(n) - n / 2.0
    xs = np.meshgrid(*([x]*ndim), indexing="ij")
    xs_sq = reduce(lambda x,y:x+y*y, xs, 0.0)

    # phi is quadratic on all dimension, so the target will be scaled
    # source on all dimension by (1+B)
    B = 1.0
    scale = 1 + B
    sigma = (n/30.)
    source = np.exp(-xs_sq / (2*sigma**2))
    source_copy = np.copy(source)
    phi = 0.5*B*xs_sq
    target = sb.forward(source, phi)

    target_calc = (scale**-ndim)*np.exp(-xs_sq / (2*(sigma*scale)**2))

    # accurate within 2.5*(1/n)*100%
    abs = 2.5/n if abs is None else abs
    assert target == pytest.approx(target_calc, abs=abs)

    # check the dimension of target
    assert np.ndim(target) == ndim

    # make sure the source is not changed
    assert np.all(source == source_copy)
