# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for running functional tests as scripts.

.. |eacute| unicode:: U+000E9 .. LATIN SMALL LETTER E WITH ACUTE
   :trim:
"""


import argparse
import contextlib
import enum
import inspect
import io
import json
import os
import types

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
import numpy as np
try:
    import seaborn  # pylint: disable=unused-import
except ImportError:
    seaborn = None
import six

import bezier
from bezier import _helpers


if seaborn is not None:
    seaborn.set()  # Required in `seaborn >= 0.8`
FNL_TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
_DOCS_DIR = os.path.abspath(
    os.path.join(FNL_TESTS_DIR, '..', 'docs'))
IMAGES_DIR = os.path.join(_DOCS_DIR, 'images')


def _start_line(func):
    """Get the start line (in source) of a function.

    Args:
        func (~types.FunctionType): A Python function object.

    Returns:
        int: The start line (in source).
    """
    _, line = inspect.getsourcelines(func)
    return line


def get_parser():
    """Create a command line argument parser.

    Returns:
        argparse.ArgumentParser: An argument parser for functional tests.
    """
    parser = argparse.ArgumentParser(
        description='Run functional tests.')
    parser.add_argument('--save-plot', dest='save_plot',
                        action='store_true')
    return parser


def real_roots(coeffs):
    """Get real roots of a polynomial.

    Args:
        coeffs (List[Float]): List of polynomial coefficients.

    Returns:
        numpy.ndarray: The (sorted) real roots of the polynomial.
    """
    all_roots = np.roots(coeffs)
    filtered = all_roots[all_roots.imag == 0.0].real
    return np.sort(filtered)


def _convert_float(value):
    """Convert an "exact" value to a ``float``.

    Also works recursively if ``value`` is a list.

    Assumes a value is one of the following:

    * :data:`None`
    * an integer
    * a string in C "%a" hex format for an IEEE-754 double precision number
    * a string fraction of the format "N/D"
    * a list of one of the accepted types (incl. a list)

    Args:
        value (Union[int, str, list]): Values to be converted.

    Returns:
        Union[float, list]: The converted value (or list of values).
    """
    if value is None:
        return None
    elif isinstance(value, list):
        return [_convert_float(element) for element in value]
    elif isinstance(value, six.integer_types):
        return float(value)
    elif value.startswith('0x') or value.startswith('-0x'):
        return float.fromhex(value)
    else:
        numerator, denominator = value.split('/')
        return float(numerator) / float(denominator)


@contextlib.contextmanager
def no_op_manager():
    """No-op context manager."""
    yield


def surface_id_func(intersection_info):
    """Turn info from ``surface_intersections.json`` into a test ID.

    Args:
        intersection_info (dict): An intersection value loaded from
            ``surface_intersections.json``.

    Returns:
        str: An identifier formatted from the info.
    """
    return 'surfaces {!r} and {!r} (ID: {:d})'.format(
        intersection_info['surface1'], intersection_info['surface2'],
        intersection_info['id'])


def convert_floats(info, keys):
    """Modify ``info`` in-place to convert strings to floating point numbers.

    Args:
        info (List[dict]): A list of dictionaries to be modified.
        keys (List[str]): The keys within each dictionary that contain
            floating point values to be converted from a "custom" form
            to native Python ``float`` values.
    """
    for element in info:
        for key in keys:
            if key not in element:
                continue

            converted = _convert_float(element[key])
            if isinstance(converted, list):
                converted = np.asfortranarray(converted)

            element[key] = converted


def curve_intersections_info():
    """Load curve and intersections info from JSON file.

    Returns:
        Tuple[Dict[str, dict], List[dict]]: The

        * mapping of curve info dictionaries.
        * list of intersection info dictionaries.
    """
    filename = os.path.join(FNL_TESTS_DIR, 'curves.json')
    with io.open(filename, 'r', encoding='utf-8') as file_obj:
        curve_json = json.load(file_obj)
    curves = {id_: CurveInfo.from_json(id_, info)
              for id_, info in six.iteritems(curve_json)}

    filename = os.path.join(FNL_TESTS_DIR, 'curve_intersections.json')
    with io.open(filename, 'r', encoding='utf-8') as file_obj:
        intersections_json = json.load(file_obj)

    intersections = [CurveIntersectionInfo.from_json(info, curves)
                     for info in intersections_json]

    return curves, intersections


def surface_intersections_info():
    """Load surface and intersections info from JSON file.

    Returns:
        Tuple[Dict[str, dict], List[dict]]: The

        * mapping of surface info dictionaries.
        * list of intersection info dictionaries.
    """
    filename = os.path.join(FNL_TESTS_DIR, 'surfaces.json')
    with io.open(filename, 'r', encoding='utf-8') as file_obj:
        surfaces = json.load(file_obj)
    convert_floats(six.itervalues(surfaces), keys=['control_points'])

    filename = os.path.join(FNL_TESTS_DIR, 'surface_intersections.json')
    with io.open(filename, 'r', encoding='utf-8') as file_obj:
        intersections = json.load(file_obj)
    keys = ['intersections', 'start_params', 'end_params']
    convert_floats(intersections, keys=keys)

    return surfaces, intersections


class Config(object):
    """Run-time configuration.

    This is a mutable stand-in to allow test set-up to modify
    global state.
    """

    def __init__(self):
        self.running = False
        self.save_plot = False
        self.current_test = None
        self.parser = get_parser()
        self._wiggle = 8

    def _run(self, mod_globals):
        """Run all tests, in source order.

        Args:
            mod_globals (dict): The globals from a module.
        """
        found = []
        for key, value in six.iteritems(mod_globals):
            if not key.lower().startswith('test'):
                continue
            if not isinstance(value, types.FunctionType):
                continue
            found.append(value)

        found.sort(key=_start_line)

        for func in found:
            self.current_test = func.__name__
            func()

    @contextlib.contextmanager
    def wiggle(self, wiggle):
        """Make the context use a temporary wiggle room.

        Args:
            wiggle (int): The temporary amount of wiggle room.

        Yields:
            Config: the current configuration.
        """
        old_wiggle = self._wiggle
        try:
            self._wiggle = wiggle
            yield self
        finally:
            self._wiggle = old_wiggle

    def assert_close(self, approximated, exact):
        """Assert two values are close, with the local configuration in place.

        Args:
            approximated (float): The value that was computed.
            exact (float): The expected value.
        """
        msg = '{} ~= {} to {:d} bits'.format(
            approximated.hex(), exact.hex(), self._wiggle)
        assert _helpers.ulps_away(
            exact, approximated, num_bits=self._wiggle), msg

    def run(self, mod_globals):
        """Run all tests, in source order.

        Args:
            mod_globals (dict): The globals from a module.
        """
        running = self.running
        save_plot = self.save_plot
        try:
            self.running = True
            args = self.parser.parse_args()
            self.save_plot = args.save_plot
            self._run(mod_globals)
        finally:
            self.running = running
            self.save_plot = save_plot
            self.current_test = None

    def save_fig(self, extra=''):
        """Save the current figure.

        Uses the ``current_test`` for the filename and puts it
        in the ``${GIT_ROOT}/docs/images`` directory.

        Args:
            extra (Optional[str]): Extra information to put in the filename.
                Filename defaults to ``{current_test}.png`` but if ``extra``
                is passed, it will be ``{current_test}{extra}.png``.
        """
        filename = '{}{}.png'.format(self.current_test, extra)
        path = os.path.join(IMAGES_DIR, filename)
        plt.savefig(path, bbox_inches='tight')
        print('Saved {}'.format(filename))


class CurveInfo(object):  # pylint: disable=too-few-public-methods
    r"""Information about a curve from ``curves.json``.

    These are expected to have three keys:

    * ``control_points``: A list of ``x-y`` coordinates of the control points
      in the curve. The coordinates themselves can be integers, stringified
      fractions or stringified IEEE-754 values (``%a`` format).
    * ``note`` (optional): Description of the curve / curve segment.
    * ``implicitized`` (optional): The algebraic curve that contains
      this B |eacute| zier curve as a segment. (Only provided if the curve
      comes from rational control points.) For example, for "curve 2"

      .. math::

         x(s) = \frac{9 - 8 s}{8}
         y(s) = \frac{(2 s - 1)^2}{2}

      so we have

      .. math::

         8 x = 9 - 8 s \Longrightarrow 8 s - 4 = 5 - 8 x
         2 y = (2 s - 1)^2 \Longrightarrow 32 y = (8 s - 4)^2
         \Longrightarrow 32 y = (5 - 8 x)^2
         \Longrightarrow 25 - 32 y - 80 x + 64 x^2 = 0

      and this implicitized algebraic curve corresponds to

      .. code-block:: python

         [
             [ 25, 0, 0],
             [-32, 0, 1],
             [-80, 1, 0],
             [ 64, 2, 0],
         ]

    This representation is a list of triples of integers
    ``coefficient, degree_x, degree_y`` where ``degree_x`` and ``degree_y``
    are non-negative. Though it's not required, we also have
    ``coefficient != 0`` and the triples are sorted by total degree
    (``degree_x + degree_y``) and then by ``degree_x`` to break ties.

    In addition, each curve comes with an ID from a dictionary, i.e.
    ``curves.json`` uses ID keys to identify the curves, rather than just
    having a list of curve info.

    Args:
        id_ (str): The ID of the curve.
        control_points (numpy.ndarray): The control points.
        implicitized (Optional[List[List[int]]]): The coefficient triples
            defining the algebraic curve that contains the
            B |eacute| zier curve.
        note (Optional[str]): A note about the curve (e.g. what is it
            related to).
    """

    def __init__(self, id_, control_points, implicitized=None, note=None):
        self.id_ = id_
        self.control_points = control_points
        self.curve = bezier.Curve.from_nodes(control_points, _copy=False)
        self.implicitized = implicitized
        self.note = note

    @classmethod
    def from_json(cls, id_, info):
        """Convert JSON curve info into ``CurveInfo``.

        This involves parsing the dictionary and converting some stringified
        values (rationals and IEEE-754) to Python ``float``-s.

        Args:
            id_ (str): The ID of the curve.
            info (dict): The JSON data of the curve.

        Returns:
            .CurveInfo: The curve info parsed from the JSON.

        Raises:
            ValueError: If any of ``info`` is left unparsed.
        """
        control_points = info.pop('control_points')
        control_points = np.asfortranarray(_convert_float(control_points))
        implicitized = info.pop('implicitized', None)

        # Optional fields.
        note = info.pop('note', None)

        if info:
            raise ValueError('Unexpected keys remaining in JSON info', info)

        return cls(id_, control_points, implicitized=implicitized, note=note)


class CurveIntersectionType(enum.Enum):
    """Enum describing curve intersection."""

    coincident = 'coincident'
    """Curves lie on the same underlying algebraic curve."""

    no_intersection = 'no-intersection'
    """Curves do not intersect."""

    tangent = 'tangent'
    """Curves are tangent at the point of intersection."""

    standard = 'standard'
    """Intersection is not **any** of the other types."""


# pylint: disable=too-many-instance-attributes
class CurveIntersectionInfo(object):
    r"""Information about an intersection from ``curve_intersections.json``.

    A curve-curve intersection JSON is expected to have 8 keys:

    * ``curve1``: ID of the first curve in the intersection.
    * ``curve2``: ID of the second curve in the intersection.
    * ``id``
    * ``type``
    * ``note`` (optional): Description of the intersection / notes about how
      it behaves.
    * ``intersections``: List of pairs of "numerical" ``x-y`` values.
    * ``curve1_params``: "Numerical" curve parameters at intersections.
    * ``curve1_polys`` (optional): The (integer) coefficients of the minimal
      polynomials that determine the values in ``curve1_params``.

      For example, if the roots are

      .. math::

         0 \\
         \frac{7 - \sqrt{7}}{14} \approx \mathtt{0x1.3e7b70cac040dp-2} \\
         \frac{7 + \sqrt{7}}{14} \approx \mathtt{0x1.60c2479a9fdfap-1} \\
         1

      Then the corresponding (minimal) polynomial coefficients are:

      .. code-block:: python

         [
             [0, 1],
             [3, -14, 14],
             [3, -14, 14],
             [-1, 1],
         ]
    * ``curve2_params``: "Numerical" curve parameters at intersections.
    * ``curve2_polys`` (optional): Similar to ``curve1_polys``.

    The "numerical" values in ``intersections``, ``curve1_params`` and
    ``curve2_params`` can be integers, stringified fractions or stringified
    IEEE-754 values (``%a`` format).

    Args:
        id_ (int): The intersection ID.
        curve1_info (CurveInfo): The curve information for the first curve in
            the intersection.
        curve2_info (CurveInfo): The curve information for the second curve in
            the intersection.
        type_ (.CurveIntersectionType): Describes how the curves intersect.
        intersections (numpy.ndarray): ``Nx2`` array of ``x-y`` coordinate
            pairs of intersection points.
        curve1_params (numpy.ndarray): 1D array, the parameters along
            ``curve1`` where the intersections occur (in the same order as
            the rows of ``intersections``). These are typically called
            ``s``-parameters.
        curve2_params (numpy.ndarray): 1D array, the parameters along
            ``curve2`` where the intersections occur (in the same order as
            the rows of ``intersections``). These are typically called
            ``t``-parameters.
        curve1_polys (Optional[List[List[int]]]): The coefficients of the
            polynomials that determine the values in ``curve1_params``.
        curve2_polys (Optional[List[List[int]]]): The coefficients of the
            polynomials that determine the values in ``curve2_params``.
        note (Optional[str]): A note about the intersection (e.g. why it is
            unique / problematic).
    """

    num_params = None

    # pylint: disable=too-many-arguments
    def __init__(self, id_, curve1_info, curve2_info, type_,
                 intersections, curve1_params, curve2_params,
                 curve1_polys=None, curve2_polys=None, note=None):
        self.id_ = id_
        self.intersections = intersections
        self.type_ = type_

        self.curve1_info = curve1_info
        self.curve1_params = curve1_params
        self.curve1_polys = curve1_polys

        self.curve2_info = curve2_info
        self.curve2_params = curve2_params
        self.curve2_polys = curve2_polys

        self.note = note

        self._verify_dimensions()
        self._verify_data()
    # pylint: enable=too-many-arguments

    def _verify_dimensions(self):
        """Verify that all the dimensions are the same.

        This also sets the ``num_params`` attribute.

        Raises:
            ValueError: If one of the values is not the "expected" shape.
        """
        if self.curve1_params.ndim != 1:
            raise ValueError(
                'Expected 1-dimensional data for ``curve1_params``.')
        # Unpack into one value now that we know 1D.
        self.num_params, = self.curve1_params.shape

        shape = (self.num_params,)
        if self.curve2_params.shape != shape:
            msg = 'Expected shape {} for ``curve2_params``.'.format(shape)
            raise ValueError(msg)

        shape = (self.num_params, 2)
        if self.intersections.shape != shape:
            msg = 'Expected shape {} for ``intersections``.'.format(shape)
            raise ValueError(msg)

        if self.curve1_polys is not None:
            if len(self.curve1_polys) != self.num_params:
                raise ValueError(
                    'Unexpected number of ``curve1_polys``',
                    len(self.curve1_polys), 'Expected', self.num_params)

        if self.curve2_polys is not None:
            if len(self.curve2_polys) != self.num_params:
                raise ValueError(
                    'Unexpected number of ``curve2_polys``',
                    len(self.curve2_polys), 'Expected', self.num_params)

    def _verify_data(self):
        """Verify assumptions about the data.

        * The intersections are sorted by s-value.

        Raises:
            ValueError: If the assumptions are not met.
        """
        sorted_s = np.sort(self.curve1_params)
        if not np.all(sorted_s == self.curve1_params):
            raise ValueError(
                'Expected s-parameters (``curve1_params``) to be '
                'in ascending order.')

    @property
    def test_id(self):
        """str: The ID for this intersection in unit tests."""
        return 'curves {!r} and {!r} (ID: {:d})'.format(
            self.curve1_info.id_, self.curve2_info.id_, self.id_)

    @property
    def img_filename(self):
        """str: Filename to use when saving images for this intersection."""
        return 'curves{}_and_{}'.format(
            self.curve1_info.id_, self.curve2_info.id_)

    @property
    def params(self):
        """Get the parameters and intersection points.

        No verification is done here, rather, it's done in the
        constructor / in :meth:`from_json`.

        Returns:
            Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]: The

            * ``s``-parameters (1D ``N`` array)
            * ``t``-parameters (1D ``N`` array)
            * intersection points (2D ``N x 2`` array)
        """
        return self.curve1_params, self.curve2_params, self.intersections

    # pylint: disable=missing-return-type-doc
    @property
    def curve1(self):
        """The first B |eacute| zier curve in the intersection.

        Returns:
            ~bezier.curve.Curve: The first B |eacute| zier curve.
        """
        return self.curve1_info.curve

    @property
    def curve2(self):
        """The second B |eacute| zier curve in the intersection.

        Returns:
            ~bezier.curve.Curve: The second B |eacute| zier curve.
        """
        return self.curve2_info.curve
    # pylint: enable=missing-return-type-doc

    @classmethod
    def from_json(cls, info, curves):
        """Convert JSON curve intersection info into ``CurveIntersectionInfo``.

        This involves parsing the dictionary and converting some stringified
        values (rationals and IEEE-754) to Python ``float``-s.

        Args:
            info (dict): The JSON data of the curve intersection.
            curves (Dict[str, CurveInfo]): An already parsed dictionary of
                curve information.

        Returns:
            .CurveIntersectionInfo: The intersection info parsed from the JSON.

        Raises:
            ValueError: If any of ``info`` is left unparsed.
        """
        id_ = info.pop('id')
        curve1 = curves[info.pop('curve1')]
        curve2 = curves[info.pop('curve2')]
        type_ = CurveIntersectionType(info.pop('type'))

        intersections = np.asfortranarray(
            _convert_float(info.pop('intersections')))
        curve1_params = np.asfortranarray(
            _convert_float(info.pop('curve1_params')))
        curve2_params = np.asfortranarray(
            _convert_float(info.pop('curve2_params')))

        if intersections.size == 0:
            intersections = intersections.reshape((0, 2))

        # Optional fields.
        curve1_polys = info.pop('curve1_polys', None)
        curve2_polys = info.pop('curve2_polys', None)
        note = info.pop('note', None)

        if info:
            raise ValueError('Unexpected keys remaining in JSON info', info)

        return cls(
            id_, curve1, curve2, type_, intersections,
            curve1_params, curve2_params,
            curve1_polys=curve1_polys, curve2_polys=curve2_polys, note=note)
# pylint: enable=too-many-instance-attributes
