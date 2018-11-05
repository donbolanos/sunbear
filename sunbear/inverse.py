import numpy as np
from scipy.interpolate import interpn
from sunbear.calculus.diff import grad, det_hess
from sunbear.forward import _get_full_potential, _get_idx
from sunbear.gradopt import Momentum

def inverse(source, target, gradopt_obj=None):
    """
    Get the normalized deflection potential given the source and target density
    distribution.
    The mapping from source coordinate, $x$, to the target coordinate, $y$, is
    given by:

    $$
    y = x + \nabla phi(x).
    $$

    The coordinate in i-th dimension is given by `np.arange(source.shape[i])`.

    Parameters
    ----------
    * `source` : numpy.ndarray
        The source density distribution in n-dimensional array.
    * `target` : numpy.ndarray
        The target density distribution in n-dimensional array. `source` and
        `target` must have the same shape.
    * `gradopt_obj` : sunbear.gradopt.GradOptInterface obj, optional
        The solver object to solve the gradient descent problem. The default
        is sunbear.gradopt.Momentum.

    Returns
    -------
    * numpy.ndarray
        The mapping potential given above. It will have the same shape as
        `source`.
    """
    # convert to numpy array
    source = np.asarray(source)
    target = np.asarray(target)
    # check the shapes
    if source.shape != target.shape:
        raise ValueError("The source and target must have the same shape.")

    # initialize phi0
    phi0 = np.zeros_like(source)
    u0, _, phi0_pad = _get_full_potential(phi0)
    x = np.array([grad(u0, axis=i) for i in range(ndim)])
    ndim = np.ndim(source)
    pts = tuple([x[_get_idx(ndim, i, slice(None,None,None), 0)] \
        for i in range(ndim)])

    # functions to get the loss function and the gradient
    def grad_phi_pad(phi_pad):
        u = u0 + phi_pad

        # calculate the determinant of the hessian
        det_hess_s = det_hess(u)

        # get the displacement in (n x D) format
        y = np.array([grad(u , axis=i) for i in range(ndim)])

        # get the target density on the source plane
        interp = lambda s: interpn(pts, s.flatten(), y, "linear").\
            reshape(s.shape)
        target_s = interp(target)

        # calculate the dudt based on Sulman (2011)
        dudt_interior = np.log(np.abs(source / (target_s * det_hess_s)))
        dudt = np.zeros_like(u)
        # we don't want the gradient on the edge changed
        idx_interior = tuple([slice(3,-3,None)]*ndim)
        idx_interior2 = tuple([slice(2,-2,None)]*ndim)
        dudt[idx_interior] = dudt_interior[idx_interior2]

        # handle nan and inf values
        dudt[np.isnan(dudt)] = 0.0
        dudt[np.isinf(dudt)] = 0.0

        # error and the gradient
        f = np.mean(dudt.flatten()**2)
        return f, dudt

    # set up the solver object and solve it
    opt = Momentum() if gradopt_obj is None else gradopt_obj
    phi_pad = opt.solve(grad_phi_pad, phi0_pad)
    idx_interior = tuple([slice(1,-1,None)]*ndim)
    return (phi_pad - u0)[idx_interior]