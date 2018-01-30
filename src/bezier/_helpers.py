# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generic geometry and floating point helpers.

As a convention, the functions defined here with a leading underscore
(e.g. :func:`_bbox`) have a special meaning.

Each of these functions have a Cython speedup with the exact same
interface which calls out to a Fortran implementation. The speedup
will be used if the extension can be built. The name **without** the
leading underscore will be surfaced as the actual interface (e.g.
``bbox``) whether that is the pure Python implementation or the speedup.
"""


import numpy as np
import six

try:
    from bezier import _speedup
except ImportError:  # pragma: NO COVER
    _speedup = None


_EPS = 0.5**40


def _vector_close(vec1, vec2, eps=_EPS):
    r"""Checks that two vectors are equal to some threshold.

    Does so by computing :math:`s_1 = \|v_1\|_2` and
    :math:`s_2 = \|v_2\|_2` and then checking if

    .. math::

       \|v_1 - v_2\|_2 \leq \varepsilon \min(s_1, s_2)

    where :math:`\varepsilon = 2^{-40} \approx 10^{-12}` is a fixed
    threshold. In the rare case that one of ``vec1`` or ``vec2`` is
    the zero vector (i.e. when :math:`\min(s_1, s_2) = 0`) instead
    checks that the other vector is close enough to zero:

    .. math::

       \|v_1\|_2 = 0 \Longrightarrow \|v_2\|_2 \leq \varepsilon

    .. note::

       This function assumes that both vectors have finite values,
       i.e. that no NaN or infinite numbers occur. NumPy provides
       :func:`np.allclose` for coverage of **all** cases.

    .. note::

       There is also a Fortran implementation of this function, which
       will be used if it can be built.

    Args:
        vec1 (numpy.ndarray): First vector for comparison.
        vec2 (numpy.ndarray): Second vector for comparison.
        eps (float): Error threshold. Defaults to :math:`2^{-40}`.

    Returns:
        bool: Flag indicating if they are close to precision.
    """
    # NOTE: We assume the caller sends a 1xD vector. We turn it into
    #       a one-dimensional vector so NumPy doesn't use a matrix norm.
    size1 = np.linalg.norm(vec1[0, :], ord=2)
    size2 = np.linalg.norm(vec2[0, :], ord=2)
    if size1 == 0:
        return size2 <= eps
    elif size2 == 0:
        return size1 <= eps
    else:
        upper_bound = eps * min(size1, size2)
        return np.linalg.norm(vec1[0, :] - vec2[0, :], ord=2) <= upper_bound


def _in_interval(value, start, end):
    """Checks if a ``value`` is an interval (inclusive).

    .. note::

       The current implementation does the most basic check,
       however, in the future, a more generic check may be desired
       that allows wiggle room around the endpoints to account
       for round-off.

    .. note::

       There is also a Fortran implementation of this function, which
       will be used if it can be built.

    Args:
        value (float): The value to check.
        start (float): The (inclusive) start of the interval.
        end (float): The (inclusive) end of the interval.

    Returns:
        bool: Indicating if the value is in the interval.
    """
    return start <= value <= end


def _bbox(nodes):
    """Get the bounding box for set of points.

    .. note::

       There is also a Fortran implementation of this function, which
       will be used if it can be built.

    Args:
       nodes (numpy.ndarray): A set of points.

    Returns:
        Tuple[float, float, float, float]: The left, right,
        bottom and top bounds for the box.
    """
    left, bottom = np.min(nodes, axis=0)
    right, top = np.max(nodes, axis=0)
    return left, right, bottom, top


def _contains_nd(nodes, point):
    r"""Predicate indicating if a point is within a bounding box.

    Like :func:`contains` but supports points in arbitrary dimension.
    Unlike :func:`contains`, this function directly uses ``<=`` and
    ``>=`` for comparison (:func:`contains` uses :func:`in_interval`).

    .. note::

       There is also a Fortran implementation of this function, which
       will be used if it can be built.

    Args:
       nodes (numpy.ndarray): A set of points.
       point (numpy.ndarray): A 1D NumPy array representing a point
           in the same dimension as ``nodes``.

    Returns:
        bool: Indicating containment.
    """
    min_vals = np.min(nodes, axis=0)
    if not np.all(min_vals <= point):
        return False

    max_vals = np.max(nodes, axis=0)
    if not np.all(point <= max_vals):
        return False

    return True


def _cross_product(vec0, vec1):
    r"""Compute the cross product of vectors in :math:`\mathbf{R}^2`.

    Utilizes the fact that

    .. math::

       \left[\begin{array}{c} A \\ B \\ 0 \end{array}\right] \times
           \left[\begin{array}{c} C \\ D \\ 0 \end{array}\right] =
           \left[\begin{array}{c} 0 \\ 0 \\ AD - BC \end{array}\right]

    and just returns the :math:`z` component.

    .. note::

       There is also a Fortran implementation of this function, which
       will be used if it can be built.

    Args:
        vec0 (numpy.ndarray): A vector as a 1x2 NumPy array.
        vec1 (numpy.ndarray): A vector as a 1x2 NumPy array.

    Returns:
        float: The cross product (or rather, its :math:`z` component).
    """
    return vec0[0, 0] * vec1[0, 1] - vec0[0, 1] * vec1[0, 0]


def _ulps_away(value1, value2, num_bits=1):
    r"""Determines if ``value1`` is within ``n`` ULPs of ``value2``.

    Uses ``np.spacing`` to determine the unit of least precision (ULP)
    for ``value1`` and then checks that the different between the values
    does not exceed ``n`` ULPs.

    When ``value1 == 0`` or ``value2 == 0``, we instead check that the other
    is less than :math:`2^{-40}` (``_EPS``) in magnitude.

    .. note::

       There is also a Fortran implementation of this function, which
       will be used if it can be built.

    Args:
        value1 (float): The first value that being compared.
        value2 (float): The second value that being compared.
        num_bits (Optional[int]): The number of bits allowed to differ.
            Defaults to ``1``.

    Returns:
        bool: Predicate indicating if the values agree to ``n`` bits.
    """
    if value1 == 0.0:
        return abs(value2) < _EPS
    elif value2 == 0.0:
        return abs(value1) < _EPS
    else:
        local_epsilon = np.spacing(value1)  # pylint: disable=no-member
        return abs(value1 - value2) <= num_bits * abs(local_epsilon)


def matrix_product(mat1, mat2):
    """Compute the product of two Fortran contiguous matrices.

    This is to avoid the overhead of NumPy converting to C-contiguous
    before computing a matrix product.

    Does so via ``A B = (B^T A^T)^T`` since ``B^T`` and ``A^T`` will be
    C-contiguous without a copy, then the product ``P = B^T A^T`` will
    be C-contiguous and we can return the view ``P^T`` without a copy.

    Args:
        mat1 (numpy.ndarray): The left-hand side matrix.
        mat2 (numpy.ndarray): The right-hand side matrix.

    Returns:
        numpy.ndarray: The product of the two matrices.
    """
    return np.dot(mat2.T, mat1.T).T


def _wiggle_interval(value, wiggle=0.5**45):
    r"""Check if ``value`` is in :math:`\left[0, 1\right]`.

    Allows a little bit of wiggle room outside the interval. Any value
    within ``wiggle`` of ``0.0` will be converted to ``0.0` and similar
    for ``1.0``.

    .. note::

       There is also a Fortran implementation of this function, which
       will be used if it can be built.

    Args:
        value (float): Value to check in interval.
        wiggle (Optional[float]): The amount of wiggle room around the
            the endpoints ``0.0`` and ``1.0``.

    Returns:
        Tuple[float, bool]: Pair of

        * The ``value`` if it's in the interval, or ``0`` or ``1``
          if the value lies slightly outside. If the ``value`` is
          too far outside the unit interval, will be NaN.
        * Boolean indicating if the ``value`` is inside the unit interval.
    """
    if -wiggle < value < wiggle:
        return 0.0, True
    elif wiggle <= value <= 1.0 - wiggle:
        return value, True
    elif 1.0 - wiggle < value < 1.0 + wiggle:
        return 1.0, True
    else:
        return np.nan, False


def cross_product_compare(start, candidate1, candidate2):
    """Compare two relative changes by their cross-product.

    This is meant to be a way to determine which vector is more "inside"
    relative to ``start``.

    .. note::

       This is a helper for :func:`_simple_convex_hull`.

    Args:
        start (numpy.ndarray): The start vector as a 1x2 NumPy array.
        candidate1 (numpy.ndarray): The first candidate vector (as a 1x2
            NumPy array).
        candidate2 (numpy.ndarray): The second candidate vector (as a 1x2
            NumPy array).

    Returns:
        float: The cross product of the two differences.
    """
    delta1 = candidate1 - start
    delta2 = candidate2 - start
    return cross_product(delta1, delta2)


def _simple_convex_hull(points):
    r"""Compute the convex hull for a set of points.

    .. _wikibooks: https://en.wikibooks.org/wiki/Algorithm_Implementation/\
                   Geometry/Convex_hull/Monotone_chain

    This uses Andrew's monotone chain convex hull algorithm and this code
    used a `wikibooks`_ implementation as motivation. tion. The code there
    is licensed CC BY-SA 3.0.

    .. note::

       There is also a Fortran implementation of this function, which
       will be used if it can be built. Note that ``scipy.spatial.ConvexHull``
       can do this as well (via Qhull), but that would require a hard
       dependency on ``scipy`` and that helper computes much more than we need.

    .. note::

       This computes the convex hull in a "naive" way. It's expected that
       internal callers of this function will have a small number of points
       so ``n log n`` vs. ``n^2`` vs. ``n`` aren't that relevant.

    Args:
        points (numpy.ndarray): A ``2 x N`` array (``float64``) of points.

    Returns:
        numpy.ndarray: The ``2 x N`` array (``float64``) of ordered points in
        the polygonal convex hull.
    """
    if points.size == 0:
        return points

    # First, drop duplicates.
    unique_points = np.unique(points, axis=1)
    _, num_points = unique_points.shape
    if num_points < 2:
        return unique_points

    # Then sort the data in "lexical" order.
    points = np.empty((2, num_points), order='F')
    for index, xy_val in enumerate(
            sorted(tuple(column) for column in unique_points.T)):
        points[:, index] = xy_val

    # Build lower hull
    lower = []
    for index in six.moves.xrange(num_points):
        point3 = points[:, index].reshape((1, 2))
        while (len(lower) >= 2 and
               cross_product_compare(lower[-2], lower[-1], point3) <= 0):
            lower.pop()
        lower.append(point3)

    # Build upper hull
    upper = []
    for index in six.moves.xrange(num_points - 1, -1, -1):
        point3 = points[:, index].reshape((1, 2))
        while (len(upper) >= 2 and
               cross_product_compare(upper[-2], upper[-1], point3) <= 0):
            upper.pop()
        upper.append(point3)

    # **Both** corners are double counted.
    size_polygon = len(lower) + len(upper) - 2
    polygon = np.empty((2, size_polygon), order='F')

    for index, point in enumerate(lower[:-1]):
        polygon[:, index] = point[0, :]
    index_start = len(lower) - 1
    for index, point in enumerate(upper[:-1]):
        polygon[:, index + index_start] = point[0, :]

    return polygon


# pylint: disable=invalid-name
if _speedup is None:  # pragma: NO COVER
    vector_close = _vector_close
    in_interval = _in_interval
    bbox = _bbox
    contains_nd = _contains_nd
    cross_product = _cross_product
    ulps_away = _ulps_away
    wiggle_interval = _wiggle_interval
    simple_convex_hull = _simple_convex_hull
else:
    vector_close = _speedup.vector_close
    in_interval = _speedup.in_interval
    bbox = _speedup.bbox
    contains_nd = _speedup.contains_nd
    cross_product = _speedup.cross_product
    ulps_away = _speedup.ulps_away
    wiggle_interval = _speedup.wiggle_interval
    simple_convex_hull = _speedup.simple_convex_hull
# pylint: enable=invalid-name
